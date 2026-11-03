import re
from typing import List, Dict, Any, Tuple
import difflib
from ..models.schemas import CandidateOutput, ReviewFinding, ConsensusSummary, ConflictItem, DeterministicValidation

class ConsensusAnalyzer:
    """
    Implements the Consensus and Validation workflow defined in Figure 4.3 of the project report.
    Compares multi-agent candidate evaluations, calculates cross-model agreement metrics,
    isolates material contradictions, and incorporates deterministic checks.
    """

    @classmethod
    def analyze(
        cls, 
        candidates: List[CandidateOutput], 
        deterministic_validation: DeterministicValidation
    ) -> Tuple[ConsensusSummary, List[ReviewFinding]]:
        if not candidates:
            return ConsensusSummary(
                consensus_score=0.0,
                strength="HIGH_DIVERGENCE",
                agreed_points=[],
                conflicts=[],
                consensus_notes="No candidate responses available to compare."
            ), []

        if len(candidates) == 1:
            cand = candidates[0]
            # FIX H6: A single agent cannot produce consensus — consensus requires ≥2 independent sources.
            # Reporting 100% consensus score from one agent is misleading.
            # We report score=None (null) and flag single_agent_mode.
            summary = ConsensusSummary(
                consensus_score=0.0,   # 0 used as sentinel for "not applicable"
                strength="SINGLE_AGENT_MODE",
                agreed_points=[f"{f.title} ({f.severity})" for f in cand.findings],
                conflicts=[],
                consensus_notes=(
                    "Single-agent baseline mode executed. "
                    "No cross-agent consensus is possible with one reviewer. "
                    "Confidence reflects only the individual agent's assessment."
                )
            )
            return summary, cand.findings

        # Multi-candidate comparison
        all_findings: List[ReviewFinding] = []
        for c in candidates:
            for f in c.findings:
                # Attach reporting agent tag
                if not f.reported_by:
                    f.reported_by = [c.persona]
                all_findings.append(f)

        # Cluster findings by semantic topic / line proximity
        clusters: Dict[str, List[ReviewFinding]] = {}
        for f in all_findings:
            key = cls._cluster_key(f)
            if key not in clusters:
                clusters[key] = []
            clusters[key].append(f)

        agreed_points: List[str] = []
        conflicts: List[ConflictItem] = []
        consolidated: List[ReviewFinding] = []

        total_topics = len(clusters)
        agreed_count = 0

        for key, group in clusters.items():
            reporters = list(set([r for f in group for r in f.reported_by]))
            first = group[0]

            # Check if there's severe severity divergence (e.g. CRITICAL vs LOW)
            severities = set(f.severity for f in group)
            has_severity_discrepancy = ("CRITICAL" in severities or "HIGH" in severities) and ("LOW" in severities or "INFO" in severities)

            # Check if deterministic validator corroborates any finding in this group
            corroborated_by_val = any(
                vuln["name"].lower() in first.title.lower() or 
                vuln["description"].lower() in first.explanation.lower() or
                (first.line_start and vuln["line"] == first.line_start)
                for vuln in deterministic_validation.static_vulnerabilities_detected
            )

            if len(reporters) > 1 and not has_severity_discrepancy:
                # Strong consensus on this issue
                agreed_count += 1
                agreed_points.append(f"{first.title} confirmed by {len(reporters)} agents ({', '.join(reporters)})")
                
                # Consolidate finding with elevated confidence
                consolidated.append(ReviewFinding(
                    id=first.id,
                    title=first.title,
                    category=first.category,
                    severity=cls._highest_severity(severities),
                    line_start=first.line_start,
                    line_end=first.line_end,
                    snippet=first.snippet,
                    explanation=f"[Consensus Verified across {len(reporters)} Agents] {first.explanation}",
                    suggested_fix=first.suggested_fix,
                    confidence=min(0.99, max(f.confidence for f in group) + 0.05),
                    reported_by=reporters
                ))
            elif has_severity_discrepancy:
                # Material conflict on risk severity
                claims = {f.reported_by[0] if f.reported_by else "Agent": f"Classified as {f.severity}" for f in group}
                resolution_rule = "Escalated to higher severity for safety; corroborated by static analysis." if corroborated_by_val else "Escalated to higher severity under fail-safe principle."
                conflicts.append(ConflictItem(
                    topic=first.title,
                    agent_claims=claims,
                    conflict_type="severity_discrepancy",
                    resolution=resolution_rule,
                    resolved_by_validation=corroborated_by_val
                ))
                consolidated.append(ReviewFinding(
                    id=first.id,
                    title=f"[Contested Severity] {first.title}",
                    category=first.category,
                    severity=cls._highest_severity(severities),
                    line_start=first.line_start,
                    line_end=first.line_end,
                    snippet=first.snippet,
                    explanation=f"{first.explanation} (Note: Agents disagreed on severity: {', '.join(severities)}).",
                    suggested_fix=first.suggested_fix,
                    confidence=0.75,
                    reported_by=reporters
                ))
            else:
                # Single agent reported this specialized aspect (e.g. security specialist saw a subtle crypto flaw)
                if corroborated_by_val:
                    agreed_count += 1
                    agreed_points.append(f"{first.title} detected by {reporters[0]} & validated by AST Engine")
                    consolidated.append(ReviewFinding(
                        id=first.id,
                        title=f"{first.title} (AST Validated)",
                        category=first.category,
                        severity=first.severity,
                        line_start=first.line_start,
                        line_end=first.line_end,
                        snippet=first.snippet,
                        explanation=f"{first.explanation} [Confirmed by Deterministic Static Check]",
                        suggested_fix=first.suggested_fix,
                        confidence=0.92,
                        reported_by=reporters
                    ))
                else:
                    consolidated.append(first)

        # Compute consensus score
        if total_topics > 0:
            consensus_score = round((agreed_count / total_topics) * 100.0, 1)
        else:
            consensus_score = 100.0

        if consensus_score >= 80.0:
            strength = "STRONG_AGREEMENT"
        elif consensus_score >= 50.0:
            strength = "MODERATE_AGREEMENT"
        else:
            strength = "HIGH_DIVERGENCE_FLAGGED"

        summary = ConsensusSummary(
            consensus_score=consensus_score,
            strength=strength,
            agreed_points=agreed_points,
            conflicts=conflicts,
            consensus_notes=(
                f"Evaluated {len(candidates)} distinct AI specialist candidate streams across {total_topics} distinct concern vectors. "
                f"Agreement reached on {agreed_count}/{total_topics} topics ({consensus_score}%). "
                f"{len(conflicts)} material discrepancies isolated and mediated through deterministic AST/safety rules."
            )
        )

        # Sort consolidated findings by severity
        severity_weight = {"CRITICAL": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2, "INFO": 1}
        consolidated.sort(key=lambda x: severity_weight.get(x.severity, 0), reverse=True)

        return summary, consolidated

    @staticmethod
    def _cluster_key(f: ReviewFinding) -> str:
        # Group by category and normalized title key words
        words = set(re.findall(r"\w{4,}", f.title.lower()))
        simplified_title = "_".join(sorted(list(words))[:3]) if words else "general"
        line_bucket = (f.line_start // 5) if f.line_start else 0
        return f"{f.category}_{simplified_title}_{line_bucket}"

    @staticmethod
    def _highest_severity(severities: set[str]) -> str:
        for s in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            if s in severities:
                return s
        return "MEDIUM"
