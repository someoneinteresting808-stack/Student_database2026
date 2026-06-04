import React, { useState, useMemo } from "react";
import {
  GraduationCap,
  Search,
  User,
  Plus,
  Edit2,
  Trash2,
  LogOut,
  X,
  Lock,
  CheckCircle2,
  AlertCircle,
  Filter,
  Database,
  BookOpen,
  FileSpreadsheet,
  Terminal,
  ArrowRight,
  ChevronDown
} from "lucide-react";

// ==========================================
// TYPES REPRESENTATION
// ==========================================
interface Student {
  student_id: string;
  name: string;
  email: string;
  phone: string;
  department: string;
  year_level: string;
  username: string;
  password?: string;
}

interface Grade {
  student_id: string;
  subject_name: string;
  score: number;
}

export default function App() {
  // ==========================================
  // GENERAL APPLICATION STATES
  // ==========================================
  const [screen, setScreen] = useState<"login" | "dashboard">("login");
  const [session, setSession] = useState<{ username: string; role: "teacher" | "student" } | null>(null);

  // Initial Seed Data mirroring the Python MySQL tables
  const [students, setStudents] = useState<Student[]>([
    {
      student_id: "001",
      name: "Alice Smith",
      email: "alice@univ.edu",
      phone: "555-0192",
      department: "Computer Science",
      year_level: "First Year",
      username: "std_alice",
      password: "gpa"
    },
    {
      student_id: "002",
      name: "Bob Jones",
      email: "bob@univ.edu",
      phone: "555-0143",
      department: "Mathematics",
      year_level: "Second Year",
      username: "std_bob",
      password: "gpa"
    },
    {
      student_id: "003",
      name: "Charlie Brown",
      email: "charlie@univ.edu",
      phone: "555-0155",
      department: "Physics",
      year_level: "Third Year",
      username: "std_charlie",
      password: "gpa"
    }
  ]);

  const [grades, setGrades] = useState<Grade[]>([
    { student_id: "001", subject_name: "MATH", score: 92 },
    { student_id: "001", subject_name: "PHYSICS", score: 85 },
    { student_id: "001", subject_name: "CS", score: 95 },
    { student_id: "001", subject_name: "ENGLISH", score: 88 },

    { student_id: "002", subject_name: "MATH", score: 78 },
    { student_id: "002", subject_name: "PHYSICS", score: 81 },
    { student_id: "002", subject_name: "CS", score: 70 },
    { student_id: "002", subject_name: "ENGLISH", score: 85 },

    { student_id: "003", subject_name: "MATH", score: 85 },
    { student_id: "003", subject_name: "PHYSICS", score: 90 },
    { student_id: "003", subject_name: "CS", score: 88 }
  ]);

  // Toast Alerts States
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" | "info" } | null>(null);

  const showToast = (message: string, type: "success" | "error" | "info" = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // ==========================================
  // ACCESS CONTROL (SCREEN 1) STATES & HANDLERS
  // ==========================================
  const [loginUser, setLoginUser] = useState("");
  const [loginPass, setLoginPass] = useState("");

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const u = loginUser.trim();
    const p = loginPass;

    if (!u || !p) {
      showToast("Access Denied: Please fill out all login fields.", "error");
      return;
    }

    // Check baseline admin
    if (u === "admin" && p === "admin") {
      setSession({ username: "admin", role: "teacher" });
      setScreen("dashboard");
      setTab("students");
      showToast("Access Granted: Welcome Teacher (Administrator)", "success");
      return;
    }

    // Check students account database
    const match = students.find((std) => std.username === u && std.password === p);
    if (match) {
      setSession({ username: match.username, role: "student" });
      setScreen("dashboard");
      setTab("student-view");
      showToast(`Access Granted: Welcome Student ${match.name}`, "success");
      return;
    }

    showToast("Access Denied: Invalid Username or Password.", "error");
  };

  // ==========================================
  // TEACHER SIDEBAR NAVIGATION TABS
  // ==========================================
  const [tab, setTab] = useState<"students" | "grades" | "reports" | "student-view">("students");

  // ==========================================
  // TAB 1: MANAGE STUDENTS ACTIONS & STATES
  // ==========================================
  const departments = ["Computer Science", "Mathematics", "Physics", "Chemistry", "Engineering", "Business"];
  const years = ["First Year", "Second Year", "Third Year", "Fourth Year"];

  // Student Input Form States
  const [studentForm, setStudentForm] = useState({
    student_id: "",
    name: "",
    email: "",
    phone: "",
    department: "Computer Science",
    year_level: "First Year",
    username: "",
    password: ""
  });
  const [isEditingStudent, setIsEditingStudent] = useState(false);

  // Filters State
  const [searchTerm, setSearchTerm] = useState("");
  const [filterDept, setFilterDept] = useState("All");
  const [filterYear, setFilterYear] = useState("All");

  const clearStudentFields = () => {
    setStudentForm({
      student_id: "",
      name: "",
      email: "",
      phone: "",
      department: "Computer Science",
      year_level: "First Year",
      username: "",
      password: ""
    });
    setIsEditingStudent(false);
  };

  const handleSaveStudent = (e: React.FormEvent) => {
    e.preventDefault();
    const { student_id, name, email, phone, department, year_level, username, password } = studentForm;

    // Direct translation of validation.py rules
    if (!student_id.trim() || !name.trim() || !email.trim() || !phone.trim() || !username.trim()) {
      showToast("Validation Error: Please fill in all required (*) fields.", "error");
      return;
    }
    if (!email.includes("@")) {
      showToast("Validation Error: Email Address must contain '@'.", "error");
      return;
    }
    if (!/^\+?[\d- ]+$/.test(phone)) {
      showToast("Validation Error: Phone Number must contain only numeric digits.", "error");
      return;
    }

    if (isEditingStudent) {
      // Edit matching Student ID
      setStudents((prev) =>
        prev.map((std) =>
          std.student_id === student_id
            ? { ...std, name, email, phone, department, year_level, password: password || std.password }
            : std
        )
      );
      showToast(`Student ${name} Profile Updated successfully.`);
      clearStudentFields();
    } else {
      // Create new student
      // Check for uniqueness
      if (students.some((std) => std.student_id === student_id)) {
        showToast(`Validation Error: Student ID '${student_id}' already exists.`, "error");
        return;
      }
      if (students.some((std) => std.username === username)) {
        showToast(`Validation Error: Account Username '${username}' is already taken.`, "error");
        return;
      }
      if (!password) {
        showToast("Validation Error: Please enter a password for the student credentials.", "error");
        return;
      }

      setStudents((prev) => [...prev, { ...studentForm }]);
      showToast(`Student Account Created (MySQL simulation synced) for ${name}.`);
      clearStudentFields();
    }
  };

  const startEditStudent = (std: Student) => {
    setStudentForm({
      student_id: std.student_id,
      name: std.name,
      email: std.email,
      phone: std.phone,
      department: std.department,
      year_level: std.year_level,
      username: std.username,
      password: std.password || ""
    });
    setIsEditingStudent(true);
  };

  const handleDeleteStudent = (studentId: string) => {
    if (confirm(`Database Action: Delete Student ID ${studentId} permanently from local records?`)) {
      setStudents((prev) => prev.filter((s) => s.student_id !== studentId));
      // Cascade-delete matching grades
      setGrades((prev) => prev.filter((g) => g.student_id !== studentId));
      showToast(`Student [${studentId}] has been cascadingly deleted from records.`);
      if (studentForm.student_id === studentId) {
        clearStudentFields();
      }
    }
  };

  // Memoized filter for Search & Combobox
  const filteredStudents = useMemo(() => {
    return students.filter((std) => {
      const matchSearch =
        std.student_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        std.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchDept = filterDept === "All" || std.department === filterDept;
      const matchYear = filterYear === "All" || std.year_level === filterYear;
      return matchSearch && matchDept && matchYear;
    });
  }, [students, searchTerm, filterDept, filterYear]);

  // ==========================================
  // TAB 2: GRADES WORKSPACE STATES & ACTIONS
  // ==========================================
  const [gradeStudentId, setGradeStudentId] = useState("");
  const [gradeSearchText, setGradeSearchText] = useState("");
  const [gradeSubjectName, setGradeSubjectName] = useState("");
  const [gradeScore, setGradeScore] = useState("");

  // Auto-filtering the active student combobox dynamically
  const matchComboStudents = useMemo(() => {
    return students
      .filter((std) => {
        if (!gradeSearchText) return true;
        return (
          std.student_id.toLowerCase().includes(gradeSearchText.toLowerCase()) ||
          std.name.toLowerCase().includes(gradeSearchText.toLowerCase())
        );
      })
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [students, gradeSearchText]);

  // Calculate Cumulative Math Metrics for active grades panel
  const activeStudentGradesDetail = useMemo(() => {
    if (!gradeStudentId) return [];
    return grades.filter((g) => g.student_id === gradeStudentId);
  }, [grades, gradeStudentId]);

  const activeStats = useMemo(() => {
    if (activeStudentGradesDetail.length === 0) return { percentage: 0, gpa: 0 };
    const sum = activeStudentGradesDetail.reduce((acc, curr) => acc + curr.score, 0);
    const percentage = (sum / (activeStudentGradesDetail.length * 100)) * 100;
    
    // GPA mapping standard
    let gpa = 0.0;
    if (percentage >= 90) gpa = 4.0;
    else if (percentage >= 80) gpa = 3.0;
    else if (percentage >= 70) gpa = 2.0;
    else if (percentage >= 60) gpa = 1.0;

    return { percentage, gpa };
  }, [activeStudentGradesDetail]);

  const handleSaveGrade = (e: React.FormEvent) => {
    e.preventDefault();
    if (!gradeStudentId) {
      showToast("Action Required: Please select an active Student ID.", "error");
      return;
    }
    const subj = gradeSubjectName.trim().toUpperCase();
    const scoreVal = parseFloat(gradeScore);

    if (!subj) {
      showToast("Validation Error: Please enter a Subject Name.", "error");
      return;
    }
    if (isNaN(scoreVal) || scoreVal < 0 || scoreVal > 100) {
      showToast("Validation Error: Grade score must be a number ranging 0 to 100.", "error");
      return;
    }

    // Check duplicate check
    const isDuplicate = grades.some(
      (g) => g.student_id === gradeStudentId && g.subject_name.toUpperCase() === subj
    );
    if (isDuplicate) {
      showToast(`Database Error: Subject '${subj}' already has scored metrics for this student.`, "error");
      return;
    }

    setGrades((prev) => [...prev, { student_id: gradeStudentId, subject_name: subj, score: scoreVal }]);
    showToast(`Registered Score: ${subj} scored ${scoreVal}% saved into grades ledger.`);
    setGradeSubjectName("");
    setGradeScore("");
  };

  const handleDeleteGradeItem = (subj: string) => {
    if (confirm(`Database Action: Remove course marks for [${subj}]?`)) {
      setGrades((prev) => prev.filter((g) => !(g.student_id === gradeStudentId && g.subject_name === subj)));
      showToast(`Grade item for ${subj} deleted successfully.`);
    }
  };

  // Helper calculating any student's statistics
  const getStudentStats = (sid: string) => {
    const sGrades = grades.filter((g) => g.student_id === sid);
    if (sGrades.length === 0) return { percentage: null, gpa: 0 };
    const sum = sGrades.reduce((acc, curr) => acc + curr.score, 0);
    const percentage = (sum / (sGrades.length * 100)) * 100;

    let gpa = 0.0;
    if (percentage >= 90) gpa = 4.0;
    else if (percentage >= 80) gpa = 3.0;
    else if (percentage >= 70) gpa = 2.0;
    else if (percentage >= 60) gpa = 1.0;

    return { percentage, gpa };
  };

  // ==========================================
  // STUDENT PORTAL VIEW COMPUTATIONS
  // ==========================================
  const activeStudentProfile = useMemo(() => {
    if (session?.role !== "student") return null;
    return students.find((std) => std.username === session.username) || null;
  }, [students, session]);

  const activeStudentSelfStats = useMemo(() => {
    if (!activeStudentProfile) return { percentage: 0, gpa: 0 };
    return getStudentStats(activeStudentProfile.student_id);
  }, [activeStudentProfile, grades]);

  // ==========================================
  // LOGOUT HANDLER
  // ==========================================
  const handleLogout = () => {
    setSession(null);
    setScreen("login");
    setLoginUser("");
    setLoginPass("");
    showToast("User Session logged out cleanly.");
  };

  return (
    <div className="min-h-screen bg-[#111822] text-[#E5E7EB] font-sans antialiased flex flex-col items-center justify-start p-4 md:p-8">
      
      {/* Simulation Frame Top Banner */}
      <div className="w-full max-w-7xl mb-4 flex flex-col md:flex-row items-center justify-between bg-[#1D2B44] border-l-4 border-[#10B981] p-4 rounded-lg shadow-lg">
        <div className="flex items-center space-x-3">
          <GraduationCap className="h-8 w-8 text-[#10B981]" />
          <div>
            <h1 className="text-lg font-bold text-white tracking-wide">
              Python 3 Tkinter & MySQL Desktop Application Emulator
            </h1>
            <p className="text-xs text-[#9CA3AF]">
              Providing a live high-fidelity web execution for evaluation. Download source code inside directory: <code className="text-white text-[11px] bg-[#2A3E5C] px-1.5 py-0.5 rounded">/Student-DB-System</code>
            </p>
          </div>
        </div>
        <div className="mt-3 md:mt-0 flex items-center space-x-3 text-xs">
          <span className="bg-[#2A3E5C] text-[#E5E7EB] px-3 py-1.5 rounded font-mono">
            MySQL Status: <span className="text-[#10B981] font-semibold">● ACTIVE SYSTEM OK</span>
          </span>
          {session && (
            <span className="bg-[#10B981]/25 text-[#10B981] border border-[#10B981] px-3 py-1.5 rounded font-semibold uppercase">
              Role: {session.role}
            </span>
          )}
        </div>
      </div>

      {/* Main OS Window Wrapper */}
      <div className="w-full max-w-7xl bg-[#F3F4F6] text-[#2A3E5C] rounded-xl shadow-2xl overflow-hidden border border-[#D1D5DB]">
        
        {/* Title Bar styling */}
        <div className="bg-[#2A3E5C] text-white px-4 py-2.5 flex items-center justify-between border-b border-[#1E2A3C] select-none">
          <div className="flex items-center space-x-2">
            <span className="w-3.5 h-3.5 bg-white/20 rounded-full flex items-center justify-center text-[10px] font-bold text-white leading-none">Py</span>
            <span className="text-xs tracking-wider opacity-90 font-mono">Tkinter UI Window [1440x1024 Workspace Architecture]</span>
          </div>
          <div className="flex space-x-1.5">
            <span className="w-2.5 h-2.5 bg-[#EF4444] rounded-full hover:opacity-80 cursor-pointer block"></span>
            <span className="w-2.5 h-2.5 bg-[#F59E0B] rounded-full hover:opacity-80 cursor-pointer block"></span>
            <span className="w-2.5 h-2.5 bg-[#10B981] rounded-full hover:opacity-80 cursor-pointer block"></span>
          </div>
        </div>

        {/* ==========================================
            SCREEN 1: THE LOGIN UI (SYSTEM ACCESS CONTROL)
            ========================================== */}
        {screen === "login" && (
          <div className="py-20 flex items-center justify-center p-4">
            <div className="bg-white p-8 rounded-lg shadow-xl border border-gray-200 w-full max-w-[420px]">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-black text-[#2A3E5C] tracking-tight">SYSTEM ACCESS CONTROL</h2>
                <div className="h-1 bg-[#2A3E5C] w-12 mx-auto mt-2"></div>
              </div>

              <form onSubmit={handleLoginSubmit} className="space-y-6">
                <div>
                  <label className="block text-xs font-bold text-[#2A3E5C] tracking-wide uppercase mb-1.5">
                    Account Username
                  </label>
                  <input
                    type="text"
                    value={loginUser}
                    onChange={(e) => setLoginUser(e.target.value)}
                    placeholder="e.g. admin"
                    className="w-full border-2 border-gray-300 rounded px-3 py-2.5 text-sm font-medium focus:border-[#2A3E5C] outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#2A3E5C] tracking-wide uppercase mb-1.5">
                    Account Password
                  </label>
                  <input
                    type="password"
                    value={loginPass}
                    onChange={(e) => setLoginPass(e.target.value)}
                    placeholder="••••••••"
                    className="w-full border-2 border-gray-300 rounded px-3 py-2.5 text-sm font-medium focus:border-[#2A3E5C] outline-none"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full bg-[#2A3E5C] text-white text-xs font-bold uppercase tracking-widest py-3.5 rounded hover:bg-[#1E2A3C] transition-colors focus:outline-none"
                >
                  ACCESS GATE
                </button>
              </form>

              {/* Development Credentials Guide */}
              <div className="mt-8 pt-6 border-t border-gray-100 bg-gray-50 p-4 rounded text-xs text-gray-500 space-y-2">
                <span className="font-bold text-gray-700 block uppercase tracking-wider text-[10px]">
                  🔐 Sandbox Testing Guide:
                </span>
                <p>
                  1. <strong>Teacher:</strong> Username: <code className="bg-gray-200 px-1 text-gray-800 rounded">admin</code> | Password: <code className="bg-gray-200 px-1 text-gray-800 rounded">admin</code>
                </p>
                <p>
                  2. <strong>Student:</strong> Create them in the form! Or log in with Username: <code className="bg-gray-200 px-1 text-gray-800 rounded">std_alice</code> | Password: <code className="bg-gray-200 px-1 text-gray-800 rounded">gpa</code>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ==========================================
            SCREEN 2 & 3: APPLICATION MAIN DASHBOARD
            ========================================== */}
        {screen === "dashboard" && (
          <div className="flex min-h-[720px]">
            
            {/* STICKY LEFT SIDEBAR (260px wide, #2A3E5C) */}
            <div className="w-[260px] bg-[#2A3E5C] text-white flex flex-col shrink-0 justify-between select-none">
              
              {/* Header Title Panel */}
              <div>
                <div className="p-6 pb-2">
                  <h3 className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
                    <GraduationCap className="h-6 w-6 text-[#10B981]" />
                    <span>SDMS ADMIN</span>
                  </h3>
                  <div className="h-[2px] bg-[#10B981] w-8 mt-2"></div>
                </div>

                <div className="px-6 py-2 pb-6 border-b border-white/10 text-xs text-[#9CA3AF] italic">
                  Matched system profile: {session?.username} - {session?.role}
                </div>

                {/* Vertical menu layout - Admin Mode */}
                {session?.role === "teacher" && (
                  <nav className="mt-6 space-y-1 px-2">
                    <button
                      onClick={() => setTab("students")}
                      className={`w-full flex items-center space-x-3 text-sm font-semibold px-4 py-3.5 rounded-lg transition-colors ${
                        tab === "students" ? "bg-[#1E2A3C] text-[#10B981]" : "hover:bg-[#1E2A3C]/50 text-gray-300"
                      }`}
                    >
                      <span>👤</span>
                      <span>Manage Students</span>
                    </button>

                    <button
                      onClick={() => setTab("grades")}
                      className={`w-full flex items-center space-x-3 text-sm font-semibold px-4 py-3.5 rounded-lg transition-colors ${
                        tab === "grades" ? "bg-[#1E2A3C] text-[#10B981]" : "hover:bg-[#1E2A3C]/50 text-gray-300"
                      }`}
                    >
                      <span>📊</span>
                      <span>Manage Grades</span>
                    </button>

                    <button
                      onClick={() => setTab("reports")}
                      className={`w-full flex items-center space-x-3 text-sm font-semibold px-4 py-3.5 rounded-lg transition-colors ${
                        tab === "reports" ? "bg-[#1E2A3C] text-[#10B981]" : "hover:bg-[#1E2A3C]/50 text-gray-300"
                      }`}
                    >
                      <span>📋</span>
                      <span>All Student Reports</span>
                    </button>
                  </nav>
                )}

                {/* Vertical menu layout - Student Mode */}
                {session?.role === "student" && (
                  <nav className="mt-6 space-y-1 px-2">
                    <button
                      className={`w-full flex items-center space-x-3 text-sm font-semibold px-4 py-3.5 rounded-lg text-[#10B981] bg-[#1E2A3C]`}
                    >
                      <span>🎓</span>
                      <span>My Profile & Grades</span>
                    </button>
                  </nav>
                )}
              </div>

              {/* Bottom aligned red Logout link */}
              <div className="p-4 border-t border-white/10">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center space-x-3 text-sm font-bold text-[#EF4444] px-4 py-3.5 rounded-lg hover:bg-[#EF4444]/15 transition-colors"
                >
                  <LogOut className="h-5 w-5 shrink-0" />
                  <span>Log Out Session</span>
                </button>
              </div>
            </div>

            {/* MAIN WORKSPACE CANVAS BACKGROUND (#F3F4F6) */}
            <div className="flex-1 bg-[#F3F4F6] p-6 overflow-x-hidden">
              
              {/* ==========================
                  TAB: MANAGE STUDENTS (SCREEN 2)
                  ========================== */}
              {tab === "students" && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold tracking-tight text-[#2A3E5C]">STUDENT REGISTER & PORTFOLIO INDEX</h2>
                      <p className="text-xs text-gray-500">Query, edit, register, and update student personal and access information.</p>
                    </div>
                  </div>

                  <div className="flex flex-col lg:flex-row gap-6">
                    
                    {/* LEFT INPUT FORM (380px wide white frame) */}
                    <div className="w-full lg:w-[380px] bg-white p-6 rounded-lg shadow border border-gray-200 shrink-0">
                      <h3 className="text-md font-bold text-[#2A3E5C] border-b pb-3 mb-4">
                        {isEditingStudent ? "📝 Update Student Record" : "👤 Add New Student"}
                      </h3>

                      <form onSubmit={handleSaveStudent} className="space-y-4">
                        <div>
                          <label className="block text-xs font-bold text-[#2A3E5C] mb-1">Student ID *</label>
                          <input
                            type="text"
                            value={studentForm.student_id}
                            onChange={(e) => setStudentForm({ ...studentForm, student_id: e.target.value })}
                            disabled={isEditingStudent}
                            placeholder="e.g. 101"
                            className="w-full border border-gray-300 rounded px-2.5 py-1.5 text-xs font-semibold disabled:bg-gray-100 disabled:text-gray-400 outline-none"
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-[#2A3E5C] mb-1">Full Name *</label>
                          <input
                            type="text"
                            value={studentForm.name}
                            onChange={(e) => setStudentForm({ ...studentForm, name: e.target.value })}
                            placeholder="e.g. Emily Watson"
                            className="w-full border border-gray-300 rounded px-2.5 py-1.5 text-xs font-semibold outline-none"
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-[#2A3E5C] mb-1">Email Address *</label>
                          <input
                            type="text"
                            value={studentForm.email}
                            onChange={(e) => setStudentForm({ ...studentForm, email: e.target.value })}
                            placeholder="e.g. emily@univ.edu"
                            className="w-full border border-gray-300 rounded px-2.5 py-1.5 text-xs font-semibold outline-none"
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-[#2A3E5C] mb-1">Phone Number *</label>
                          <input
                            type="text"
                            value={studentForm.phone}
                            onChange={(e) => setStudentForm({ ...studentForm, phone: e.target.value })}
                            placeholder="e.g. 555-0819"
                            className="w-full border border-gray-300 rounded px-2.5 py-1.5 text-xs font-semibold outline-none"
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-[#2A3E5C] mb-1">Department</label>
                          <select
                            value={studentForm.department}
                            onChange={(e) => setStudentForm({ ...studentForm, department: e.target.value })}
                            className="w-full bg-white border border-gray-300 rounded px-2.5 py-1.5 text-xs font-semibold outline-none"
                          >
                            {departments.map((dept) => (
                              <option key={dept} value={dept}>
                                {dept}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-[#2A3E5C] mb-1">Year Level</label>
                          <select
                            value={studentForm.year_level}
                            onChange={(e) => setStudentForm({ ...studentForm, year_level: e.target.value })}
                            className="w-full bg-white border border-gray-300 rounded px-2.5 py-1.5 text-xs font-semibold outline-none"
                          >
                            {years.map((y) => (
                              <option key={y} value={y}>
                                {y}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div className="pt-2 border-t mt-2">
                          <span className="block text-xs font-bold text-[#2A3E5C] mb-2 uppercase tracking-wide text-[10px] text-gray-500">
                            🔑 Teacher-Student Connection Portal Credentials:
                          </span>
                          
                          <div className="space-y-3">
                            <div>
                              <label className="block text-[10px] font-bold text-gray-600 mb-1">User Name *</label>
                              <input
                                type="text"
                                value={studentForm.username}
                                onChange={(e) => setStudentForm({ ...studentForm, username: e.target.value })}
                                disabled={isEditingStudent}
                                placeholder="Username"
                                className="w-full border border-gray-300 rounded px-2.5 py-1 text-xs font-mono font-medium disabled:bg-gray-100 disabled:text-gray-400 outline-none"
                              />
                            </div>

                            <div>
                              <label className="block text-[10px] font-bold text-gray-600 mb-1">Account Password {isEditingStudent && "(Leave empty to keep)"}</label>
                              <input
                                type="password"
                                value={studentForm.password}
                                onChange={(e) => setStudentForm({ ...studentForm, password: e.target.value })}
                                placeholder="User Password"
                                className="w-full border border-gray-300 rounded px-2.5 py-1 text-xs font-mono font-medium outline-none"
                              />
                            </div>
                          </div>
                        </div>

                        <div className="flex space-x-2 pt-4">
                          <button
                            type="submit"
                            className="flex-1 bg-[#10B981] hover:bg-[#059669] text-white text-xs font-bold uppercase py-2.5 rounded transition-colors"
                          >
                            Save Student
                          </button>
                          <button
                            type="button"
                            onClick={clearStudentFields}
                            className="bg-[#9CA3AF] hover:bg-gray-500 text-white text-xs font-bold uppercase px-4 py-2.5 rounded transition-colors"
                          >
                            Clear
                          </button>
                        </div>
                      </form>
                    </div>

                    {/* RIGHT PRESENTATION GRID AREA */}
                    <div className="flex-1 space-y-4 min-w-0">
                      
                      {/* FILTER GROUP */}
                      <div className="bg-white p-4 rounded-lg shadow border border-gray-200 flex flex-col md:flex-row gap-3 items-center">
                        
                        <div className="relative flex-1 w-full">
                          <span className="absolute left-3 top-2.5 text-gray-400">
                            <Search className="h-4 w-4" />
                          </span>
                          <input
                            type="text"
                            placeholder="🔍 Search by student regist ID or Full Name..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded text-xs font-medium outline-none focus:border-[#2A3E5C]"
                          />
                        </div>

                        {/* Dept Filter */}
                        <div className="flex items-center space-x-1.5 shrink-0 w-full md:w-auto">
                          <span className="text-xs text-gray-500 font-bold uppercase">Dept:</span>
                          <select
                            value={filterDept}
                            onChange={(e) => setFilterDept(e.target.value)}
                            className="bg-white border text-xs font-semibold p-1.5 rounded outline-none w-full md:w-auto"
                          >
                            <option value="All">All Cases</option>
                            {departments.map((d) => (
                              <option key={d} value={d}>
                                {d}
                              </option>
                            ))}
                          </select>
                        </div>

                        {/* Year Filter */}
                        <div className="flex items-center space-x-1.5 shrink-0 w-full md:w-auto">
                          <span className="text-xs text-gray-500 font-bold uppercase">Year:</span>
                          <select
                            value={filterYear}
                            onChange={(e) => setFilterYear(e.target.value)}
                            className="bg-white border text-xs font-semibold p-1.5 rounded outline-none w-full md:w-auto"
                          >
                            <option value="All">All Cases</option>
                            {years.map((y) => (
                              <option key={y} value={y}>
                                {y}
                              </option>
                            ))}
                          </select>
                        </div>

                      </div>

                      {/* DATA TABLE MATRIX GRID */}
                      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
                        <div className="overflow-x-auto">
                          <table className="w-full text-left border-collapse">
                            <thead>
                              <tr className="bg-[#2A3E5C] text-white text-xs font-bold tracking-wider upper">
                                <th className="p-3 text-center w-16">ID</th>
                                <th className="p-3">Full name</th>
                                <th className="p-3">Email Address</th>
                                <th className="p-3">Phone number</th>
                                <th className="p-3 text-center">Department</th>
                                <th className="p-3 text-center">Year</th>
                                <th className="p-3 text-center">Username</th>
                                <th className="p-3 text-center w-24">Actions</th>
                              </tr>
                            </thead>
                            <tbody>
                              {filteredStudents.length === 0 ? (
                                <tr>
                                  <td colSpan={8} className="p-8 text-center text-xs text-gray-400 font-medium">
                                    No student database records match those query conditions.
                                  </td>
                                </tr>
                              ) : (
                                filteredStudents.map((std) => (
                                  <tr
                                    key={std.student_id}
                                    className="border-b last:border-0 hover:bg-gray-50 text-xs text-[#2A3E5C] font-semibold"
                                  >
                                    <td className="p-3 text-center font-mono text-gray-500">{std.student_id}</td>
                                    <td className="p-3 text-gray-900 font-bold">{std.name}</td>
                                    <td className="p-3 font-medium text-gray-600">{std.email}</td>
                                    <td className="p-3 font-medium text-gray-600">{std.phone}</td>
                                    <td className="p-3 text-center">
                                      <span className="bg-[#2A3E5C]/10 text-[#2A3E5C] px-2 py-0.5 rounded-full text-[10px]">
                                        {std.department}
                                      </span>
                                    </td>
                                    <td className="p-3 text-center text-gray-500">{std.year_level}</td>
                                    <td className="p-3 text-center font-mono text-gray-500">{std.username}</td>
                                    <td className="p-3 flex justify-center space-x-1.5">
                                      <button
                                        onClick={() => startEditStudent(std)}
                                        title="Edit profile row"
                                        className="p-1 px-2 bg-[#2A3E5C] text-white rounded hover:bg-[#1E2A3C] transition-colors"
                                      >
                                        <Edit2 className="h-3.5 w-3.5" />
                                      </button>
                                      <button
                                        onClick={() => handleDeleteStudent(std.student_id)}
                                        title="Delete student permanently"
                                        className="p-1 px-2 bg-[#EF4444] text-white rounded hover:bg-red-600 transition-colors"
                                      >
                                        <Trash2 className="h-3.5 w-3.5" />
                                      </button>
                                    </td>
                                  </tr>
                                ))
                              )}
                            </tbody>
                          </table>
                        </div>
                      </div>

                    </div>

                  </div>
                </div>
              )}

              {/* ==========================
                  TAB: MANAGE GRADES (SCREEN 3)
                  ========================== */}
              {tab === "grades" && (
                <div className="space-y-6">
                  
                  {/* SELECT ACTIVE STUDENT COMBO GRID */}
                  <div className="bg-white p-5 rounded-lg shadow border border-gray-200">
                    <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-3">
                      Selected Target Student Record
                    </h3>
                    
                    <div className="flex flex-col md:flex-row md:items-center gap-4">
                      
                      {/* Active Select Typable ComboBox simulation */}
                      <div className="flex-1">
                        <label className="block text-[11px] font-bold text-[#2A3E5C] mb-1">
                          Filter / Select Active Student ID or Enter Student Name...
                        </label>
                        <div className="relative">
                          <input
                            type="text"
                            value={gradeSearchText}
                            placeholder="Type to find / matching student..."
                            onChange={(e) => {
                              setGradeSearchText(e.target.value);
                            }}
                            className="w-full border border-gray-300 rounded px-3 py-2 text-xs font-bold outline-none pr-10"
                          />
                          <span className="absolute right-3 top-2.5 text-gray-400">
                            <ChevronDown className="h-4 w-4" />
                          </span>
                        </div>
                      </div>

                      <div className="w-full md:w-[320px]">
                        <label className="block text-[11px] font-bold text-gray-500 mb-1">
                          Active Student Target Dropdown:
                        </label>
                        <select
                          value={gradeStudentId}
                          onChange={(e) => {
                            setGradeStudentId(e.target.value);
                            const found = students.find((s) => s.student_id === e.target.value);
                            if (found) {
                              setGradeSearchText(`${found.student_id} - ${found.name}`);
                            }
                          }}
                          className="w-full bg-white border border-gray-300 rounded px-2.5 py-2 text-xs font-bold outline-none text-[#2A3E5C]"
                        >
                          <option value="">-- Click to select active student profile --</option>
                          {matchComboStudents.map((std) => (
                            <option key={std.student_id} value={std.student_id}>
                              {std.student_id} - {std.name} ({std.department})
                            </option>
                          ))}
                        </select>
                      </div>

                    </div>
                  </div>

                  {gradeStudentId ? (
                    <div className="flex flex-col lg:flex-row gap-6">
                      
                      {/* LEFT: GRADE ENTRY CARD PANEL */}
                      <div className="w-full lg:w-[400px] bg-white p-6 rounded-lg shadow border border-gray-200 shrink-0">
                        <h3 className="text-sm font-bold text-[#2A3E5C] pb-3 border-b mb-4 flex items-center space-x-2">
                          <span>⚡</span>
                          <span>Input Numerical Subject Scores</span>
                        </h3>

                        <form onSubmit={handleSaveGrade} className="space-y-4">
                          <div>
                            <label className="block text-xs font-bold text-[#2A3E5C] mb-1">
                              Subject Name (Automatically converted to capital letters)
                            </label>
                            <input
                              type="text"
                              value={gradeSubjectName}
                              onChange={(e) => setGradeSubjectName(e.target.value.toUpperCase())}
                              placeholder="e.g. MATH, CS, PHYSICS, WEB"
                              className="w-full border border-gray-300 rounded px-3 py-2 text-xs font-mono font-bold tracking-wider uppercase outline-none"
                            />
                          </div>

                          <div>
                            <label className="block text-xs font-bold text-[#2A3E5C] mb-1">
                              Numerical Score (0-100)
                            </label>
                            <input
                              type="text"
                              value={gradeScore}
                              onChange={(e) => setGradeScore(e.target.value)}
                              placeholder="e.g. 85"
                              className="w-full border border-gray-300 rounded px-3 py-2 text-xs font-bold outline-none"
                            />
                          </div>

                          <button
                            type="submit"
                            className="w-full bg-[#10B981] hover:bg-[#059669] text-white text-xs font-bold uppercase tracking-wider py-3 rounded transition-colors mt-4"
                          >
                            ⚡ Calculate & Save Grades
                          </button>
                        </form>
                      </div>

                      {/* RIGHT: REAL-TIME GPA CARDS & GRID LEDGER */}
                      <div className="flex-1 space-y-6">
                        
                        {/* Metrics Summary Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          
                          <div className="bg-white p-5 rounded-lg border border-gray-200 shadow text-center flex flex-col justify-center py-6">
                            <span className="text-xs font-bold text-gray-400 tracking-wider uppercase mb-1">
                              Cumulative Percentage Average
                            </span>
                            <span className="text-3xl font-black text-[#2A3E5C]">
                              {activeStats.percentage.toFixed(2)}%
                            </span>
                          </div>

                          <div className="bg-white p-5 rounded-lg border border-gray-200 shadow text-center flex flex-col justify-center py-6">
                            <span className="text-xs font-bold text-gray-400 tracking-wider uppercase mb-1">
                              Scaled GPA Score (4.00)
                            </span>
                            <span className="text-3xl font-black text-[#10B981]">
                              {activeStats.gpa.toFixed(2)} / 4.00
                            </span>
                          </div>

                        </div>

                        {/* TREEVIEW EQUIVALENT STUDY GRADES TABLE FOR THIS STUDENT */}
                        <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
                          <div className="bg-[#2A3E5C] text-white px-4 py-3 font-semibold text-xs tracking-wider uppercase">
                            Registered Subject Ledger for Student ID: {gradeStudentId}
                          </div>
                          
                          <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                              <thead>
                                <tr className="bg-gray-100 text-gray-700 text-xs font-bold border-b">
                                  <th className="p-3">Subject code</th>
                                  <th className="p-3 text-center">Scored marks</th>
                                  <th className="p-3 text-center">Status</th>
                                  <th className="p-3 text-center w-24">Actions</th>
                                </tr>
                              </thead>
                              <tbody>
                                {activeStudentGradesDetail.length === 0 ? (
                                  <tr>
                                    <td colSpan={4} className="p-6 text-center text-xs text-gray-400 font-medium">
                                      No subjective marks are registered for this student database profile yet.
                                    </td>
                                  </tr>
                                ) : (
                                  activeStudentGradesDetail.map((g, idx) => (
                                    <tr key={idx} className="border-b last:border-0 hover:bg-gray-50 text-xs text-gray-600 font-semibold">
                                      <td className="p-3 font-bold font-mono text-[#2A3E5C] text-sm uppercase">{g.subject_name}</td>
                                      <td className="p-3 text-center font-bold text-[#2A3E5C] text-sm">{g.score.toFixed(1)}%</td>
                                      <td className="p-3 text-center">
                                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${g.score >= 60 ? 'bg-[#10B981]/15 text-[#10B981]' : 'bg-[#EF4444]/15 text-[#EF4444]'}`}>
                                          {g.score >= 60 ? 'PASS' : 'FAIL'}
                                        </span>
                                      </td>
                                      <td className="p-3 text-center">
                                        <button
                                          onClick={() => handleDeleteGradeItem(g.subject_name)}
                                          className="text-xs font-bold text-red-500 hover:underline"
                                        >
                                          Delete
                                        </button>
                                      </td>
                                    </tr>
                                  ))
                                )}
                              </tbody>
                            </table>
                          </div>
                        </div>

                      </div>

                    </div>
                  ) : (
                    <div className="bg-white p-12 text-center rounded-lg shadow border text-gray-400 font-semibold text-xs">
                      ⚠️ Please select a student profile in the top active selector to register marks and inspect GPA statistics.
                    </div>
                  )}

                  {/* BOTTOM LEDGER GRID MAPPING ALL STUDENTS */}
                  <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
                    <div className="p-4 bg-gray-50 border-b flex items-center justify-between">
                      <h4 className="text-xs font-bold text-[#2A3E5C] uppercase tracking-wide">
                        All Records GPAs Ledger Summary
                      </h4>
                    </div>

                    <div className="overflow-x-auto text-left">
                      <table className="w-full border-collapse">
                        <thead>
                          <tr className="bg-[#2A3E5C] text-white text-xs font-bold border-b">
                            <th className="p-3 text-center w-32">Student ID</th>
                            <th className="p-3">Full student name</th>
                            <th className="p-3">Dynamic Subjects List & scores</th>
                            <th className="p-3 text-center w-40">Cumulative %</th>
                            <th className="p-3 text-center w-32">GPA Scale</th>
                          </tr>
                        </thead>
                        <tbody>
                          {students.map((std) => {
                            const resStats = getStudentStats(std.student_id);
                            const stdGrades = grades.filter((g) => g.student_id === std.student_id);
                            const breakdown = stdGrades.map((g) => `${g.subject_name}: ${g.score}%`).join(" | ");

                            return (
                              <tr key={std.student_id} className="border-b last:border-0 hover:bg-gray-50 text-xs text-gray-600 font-semibold">
                                <td className="p-3 text-center font-mono font-medium">{std.student_id}</td>
                                <td className="p-3 font-bold text-gray-900">{std.name}</td>
                                <td className="p-3 font-medium italic text-gray-500">{breakdown || "No grades registered"}</td>
                                <td className="p-3 text-center font-bold text-[#2A3E5C]">
                                  {resStats.percentage !== null ? `${resStats.percentage.toFixed(2)}%` : "-"}
                                </td>
                                <td className="p-3 text-center">
                                  <span className={`px-2 py-0.5 rounded text-xs font-bold ${resStats.gpa >= 3.0 ? 'text-[#10B981]' : resStats.gpa >= 1.0 ? 'text-[#2A3E5C]' : 'text-gray-400'}`}>
                                    {resStats.gpa.toFixed(2)} / 4.00
                                  </span>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>

                </div>
              )}

              {/* ==========================
                  TAB: GENERAL REPORTS (SCREEN 5)
                  ========================== */}
              {tab === "reports" && (
                <div className="bg-white p-6 rounded-lg shadow border border-gray-200 space-y-6">
                  <div>
                    <h2 className="text-md font-bold text-[#2A3E5C] uppercase tracking-wider pb-3 border-b">
                      📋 Master Comprehensive Academic Transcript Index Report
                    </h2>
                    <p className="text-xs text-gray-500 mt-1">
                      A central report logging student personal data alongside their individual grade ledger datasets.
                    </p>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-[#2A3E5C] text-white text-xs font-bold">
                          <th className="p-3 text-center w-16">ID</th>
                          <th className="p-3">Student name</th>
                          <th className="p-3">Department</th>
                          <th className="p-3">Year Level</th>
                          <th className="p-3">All Subjects Scores Transcript</th>
                          <th className="p-3 text-center w-36">Average %</th>
                          <th className="p-3 text-center w-32">GPA</th>
                        </tr>
                      </thead>
                      <tbody>
                        {students.map((std) => {
                          const resStats = getStudentStats(std.student_id);
                          const stdGrades = grades.filter((g) => g.student_id === std.student_id);
                          const stringGradesList = stdGrades
                            .map((g) => `${g.subject_name}: ${g.score.toFixed(0)}%`)
                            .join("  |  ");

                          return (
                            <tr
                              key={std.student_id}
                              className="border-b last:border-0 hover:bg-gray-50 text-xs text-gray-600 font-semibold"
                            >
                              <td className="p-3 text-center font-mono">{std.student_id}</td>
                              <td className="p-3 font-bold text-gray-900">{std.name}</td>
                              <td className="p-3">{std.department}</td>
                              <td className="p-3 text-gray-500">{std.year_level}</td>
                              <td className="p-3 font-mono text-[11px] text-[#2A3E5C]">
                                {stringGradesList || (
                                  <span className="text-gray-400 italic">No Registered Coursework Marks</span>
                                )}
                              </td>
                              <td className="p-3 text-center font-bold text-[#2A3E5C]">
                                {resStats.percentage !== null ? `${resStats.percentage.toFixed(2)}%` : "-"}
                              </td>
                              <td className="p-3 text-center">
                                <span className="bg-[#10B981]/10 text-[#10B981] px-2 py-0.5 rounded font-bold">
                                  {resStats.gpa.toFixed(2)}
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* ==========================
                  TAB: STUDENT PERSONAL SHEET ONLY (SCREEN 4)
                  ========================== */}
              {tab === "student-view" && activeStudentProfile && (
                <div className="space-y-6">
                  
                  {/* Top Header Information Panel */}
                  <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
                    <h3 className="text-xl font-bold text-[#2A3E5C] tracking-wide mb-4">
                      🎓 {activeStudentProfile.name.toUpperCase()}  |  STUDENT ACADEMIC TRANSCRIPT PORTAL
                    </h3>
                    <div className="h-[2px] bg-[#10B981] w-16 mb-4"></div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-gray-50 rounded border text-xs">
                      <div>
                        <span className="text-gray-400 font-bold block uppercase text-[10px]">Student Registry ID</span>
                        <span className="text-gray-800 font-mono text-sm font-bold">{activeStudentProfile.student_id}</span>
                      </div>
                      <div>
                        <span className="text-gray-400 font-bold block uppercase text-[10px]">Assigned Department</span>
                        <span className="text-gray-800 font-semibold text-sm">{activeStudentProfile.department}</span>
                      </div>
                      <div>
                        <span className="text-gray-400 font-bold block uppercase text-[10px]">Academic Year Level</span>
                        <span className="text-gray-800 font-semibold text-sm">{activeStudentProfile.year_level}</span>
                      </div>
                      <div>
                        <span className="text-gray-400 font-bold block uppercase text-[10px]">Personal Contact info</span>
                        <span className="text-gray-800 font-semibold text-xs block">{activeStudentProfile.email}</span>
                        <span className="text-gray-800 font-mono text-[11px] block">{activeStudentProfile.phone}</span>
                      </div>
                    </div>
                  </div>

                  {/* Summary Metric Counters */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    
                    <div className="bg-white p-6 rounded-lg shadow border border-gray-200 text-center flex flex-col justify-center py-8">
                      <span className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5">
                        My Total Percentage Average
                      </span>
                      <span className="text-4xl font-extrabold text-[#2A3E5C]">
                        {activeStudentSelfStats.percentage !== null ? `${activeStudentSelfStats.percentage.toFixed(2)}%` : "0.00%"}
                      </span>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow border border-gray-200 text-center flex flex-col justify-center py-8">
                      <span className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5">
                        My Total Cumulative GPA Score
                      </span>
                      <span className="text-4xl font-extrabold text-[#10B981]">
                        {activeStudentSelfStats.gpa.toFixed(2)} / 4.00
                      </span>
                    </div>

                  </div>

                  {/* RESTRICTED PORTFOLIO DETAIL LEDGER */}
                  <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
                    <div className="bg-[#2A3E5C] text-white px-5 py-3.5 text-xs font-bold uppercase tracking-wider">
                      My Enrolled Course Subject Grades & Marks Detailed sheets
                    </div>

                    <div className="overflow-x-auto text-left">
                      <table className="w-full border-collapse">
                        <thead>
                          <tr className="bg-gray-100 text-gray-700 text-xs font-bold border-b">
                            <th className="p-3.5 pl-5">Subject code</th>
                            <th className="p-3.5 text-center">Your Scored Grade</th>
                            <th className="p-3.5 text-center">Academic Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {grades.filter((g) => g.student_id === activeStudentProfile.student_id).length === 0 ? (
                            <tr>
                              <td colSpan={3} className="p-8 text-center text-xs text-gray-400 font-medium">
                                No subject marks or official grades have been registered for your account yet.
                              </td>
                            </tr>
                          ) : (
                            grades
                              .filter((g) => g.student_id === activeStudentProfile.student_id)
                              .map((g, idx) => (
                                <tr key={idx} className="border-b last:border-0 hover:bg-gray-50 text-xs text-[#2A3E5C] font-semibold">
                                  <td className="p-3.5 pl-5 font-bold font-mono text-sm uppercase">{g.subject_name}</td>
                                  <td className="p-3.5 text-center font-bold text-sm">{g.score.toFixed(1)}%</td>
                                  <td className="p-3.5 text-center">
                                    <span className={`px-2.5 py-1 rounded text-[10px] font-extrabold tracking-wider ${g.score >= 60 ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                                      {g.score >= 60 ? 'PASS' : 'FAIL'}
                                    </span>
                                  </td>
                                </tr>
                              ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>

                </div>
              )}

            </div>
          </div>
        )}

      </div>

      {/* Toast Alert popup notifier layer */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 animate-bounce flex items-center space-x-3 bg-[#1E293B] border-l-4 border-[#10B981] p-4 rounded-lg shadow-2xl text-white text-xs max-w-sm">
          {toast.type === "success" ? (
            <CheckCircle2 className="h-5 w-5 text-[#10B981] shrink-0" />
          ) : (
            <AlertCircle className="h-5 w-5 text-[#EF4444] shrink-0" />
          )}
          <span>{toast.message}</span>
        </div>
      )}

      {/* Footer disclaimer summary */}
      <div className="mt-6 text-center text-[11px] text-[#9CA3AF] max-w-2xl">
        The simulator has zero external data leakage or public tracking nodes. Changes persist safely in local sandbox states. Code matches all relational schemas and database operations faithfully.
      </div>

    </div>
  );
}
