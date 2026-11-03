import React from "react";
import { X, Award, GraduationCap, BookOpen, User, CheckCircle2, Building, Shield } from "lucide-react";

export default function AcademicInfoModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop">
      <div className="modal-card academic-modal-card">
        {/* Header */}
        <div className="modal-header">
          <div className="modal-title-wrap">
            <GraduationCap size={20} className="text-amber-400" />
            <h3 className="modal-title">Academic Bonafide & Institutional Credentials</h3>
          </div>
          <button onClick={onClose} className="modal-close-btn">
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body academic-body">
          {/* Institution Banner */}
          <div className="academic-institution-card">
            <div className="inst-seal-icon">
              <Building size={24} className="text-amber-300" />
            </div>
            <div>
              <h4 className="inst-heading">SATHYABAMA INSTITUTE OF SCIENCE AND TECHNOLOGY</h4>
              <p className="inst-subheading">
                (Deemed to be University) • Category-1 University by UGC • NAAC Accredited "A++" Grade
              </p>
              <p className="inst-dept">DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING • SCHOOL OF COMPUTING</p>
            </div>
          </div>

          {/* Project Details Grid */}
          <div className="credentials-grid">
            <div className="cred-item">
              <span className="cred-label">Project Title:</span>
              <span className="cred-val highlight-title">CODE REVIEW AGENT (NCIO Architecture)</span>
            </div>
            <div className="cred-item">
              <span className="cred-label">Degree & Term:</span>
              <span className="cred-val">Bachelor of Engineering (B.E.) • CSE • Nov 2026</span>
            </div>
            <div className="cred-item">
              <span className="cred-label">Project Authors:</span>
              <div className="students-list">
                <span className="student-badge">Barath Babu (Reg.No 44110102)</span>
                <span className="student-badge">Araveeti Shravanth Reddy (Reg.No 44110063)</span>
              </div>
            </div>
            <div className="cred-item">
              <span className="cred-label">Internal Guide:</span>
              <span className="cred-val">Dr. NANCY NOELLA, M.E., Ph.D.</span>
            </div>
            <div className="cred-item">
              <span className="cred-label">Head of the Department:</span>
              <span className="cred-val">Dr. L. LAKSHMANAN, M.E., Ph.D.</span>
            </div>
            <div className="cred-item">
              <span className="cred-label">Professional Training:</span>
              <span className="cred-val">Credo Systemz • Agentic AI Certification (July 2026 - Sept 2026)</span>
            </div>
          </div>

          {/* Core Architectural Contributions */}
          <div className="contributions-card">
            <h5 className="contrib-title">
              <Shield size={14} className="inline-icon text-cyan-400" /> Key NCIO Scientific Contributions:
            </h5>
            <ul className="contrib-list">
              <li>
                <strong>Multi-Agent Persona Dispatch:</strong> Orchestrates specialized Gemini AI personas (Security, Performance, Reliability) to evaluate code without single-model blind spots.
              </li>
              <li>
                <strong>Consensus & Conflict Analysis:</strong> Discards naive majority voting in favor of evidence-based cross-model agreement metrics and explicit disagreement mediation.
              </li>
              <li>
                <strong>Deterministic AST Grounding:</strong> Validates outputs using programmatic AST parsers and regex security heuristics to prevent hallucinations from compromising production code.
              </li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button onClick={onClose} className="btn-modal-save">
            Close Credentials
          </button>
        </div>
      </div>
    </div>
  );
}
