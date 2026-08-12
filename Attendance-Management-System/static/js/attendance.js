// Attendance Module JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const deptSelect = document.getElementById('filter_department_id');
    const yearSelect = document.getElementById('filter_year');
    const sectionSelect = document.getElementById('filter_section');
    const subjectSelect = document.getElementById('filter_subject_id');
    const btnLoadStudents = document.getElementById('btn_load_students');
    const studentListContainer = document.getElementById('student_list_container');
    const studentTableBody = document.getElementById('student_table_body');
    const btnMarkAllPresent = document.getElementById('btn_mark_all_present');
    const btnMarkAllAbsent = document.getElementById('btn_mark_all_absent');

    // 1. Fetch Subjects dynamically when Department or Year changes
    function loadSubjects() {
        if (!deptSelect || !subjectSelect) return;
        const deptId = deptSelect.value;
        const year = yearSelect ? yearSelect.value : '';

        if (!deptId) {
            subjectSelect.innerHTML = '<option value="">-- Select Subject --</option>';
            return;
        }

        fetch(`/attendance/api/subjects?department_id=${deptId}&year=${encodeURIComponent(year)}`)
            .then(res => res.json())
            .then(subjects => {
                subjectSelect.innerHTML = '<option value="">-- Select Subject --</option>';
                subjects.forEach(sub => {
                    const opt = document.createElement('option');
                    opt.value = sub.id;
                    opt.textContent = `${sub.code} - ${sub.name} (${sub.year})`;
                    subjectSelect.appendChild(opt);
                });
            })
            .catch(err => console.error('Error fetching subjects:', err));
    }

    if (deptSelect) deptSelect.addEventListener('change', loadSubjects);
    if (yearSelect) yearSelect.addEventListener('change', loadSubjects);

    // 2. Fetch Student list dynamically when Load Students button clicked
    if (btnLoadStudents) {
        btnLoadStudents.addEventListener('click', function() {
            const deptId = deptSelect.value;
            const year = yearSelect.value;
            const section = sectionSelect.value;
            const subjectId = subjectSelect.value;

            if (!deptId || !year || !section || !subjectId) {
                alert('Please select Department, Year, Section, and Subject first.');
                return;
            }

            fetch(`/attendance/api/students?department_id=${deptId}&year=${encodeURIComponent(year)}&section=${encodeURIComponent(section)}`)
                .then(res => res.json())
                .then(students => {
                    if (students.length === 0) {
                        studentTableBody.innerHTML = `
                            <tr>
                                <td colspan="5" class="text-center py-4 text-muted">
                                    <i class="fas fa-user-slash fa-2x mb-2"></i><br>
                                    No students found for ${deptSelect.options[deptSelect.selectedIndex].text}, ${year} Section ${section}.
                                </td>
                            </tr>`;
                        studentListContainer.classList.remove('d-none');
                        return;
                    }

                    studentTableBody.innerHTML = '';
                    students.forEach((st, idx) => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>${idx + 1}</td>
                            <td>
                                <div><strong class="text-dark">${st.roll_number || st.user_id_code}</strong></div>
                                <small class="text-muted font-monospace" style="font-size: 0.75rem;">Reg: ${st.register_number || 'N/A'}</small>
                            </td>
                            <td>
                                <div class="fw-semibold text-dark">${st.full_name}</div>
                                <small class="text-muted" style="font-size: 0.8rem;">${st.email}</small>
                            </td>
                            <td>
                                <div class="btn-group btn-group-sm" role="group">
                                    <input type="radio" class="btn-check" name="status_${st.id}" id="present_${st.id}" value="Present" checked>
                                    <label class="btn btn-outline-success" for="present_${st.id}">
                                        <i class="fas fa-check-circle me-1"></i> Present
                                    </label>

                                    <input type="radio" class="btn-check" name="status_${st.id}" id="absent_${st.id}" value="Absent">
                                    <label class="btn btn-outline-danger" for="absent_${st.id}">
                                        <i class="fas fa-times-circle me-1"></i> Absent
                                    </label>
                                </div>
                            </td>
                            <td>
                                <input type="text" name="remarks_${st.id}" class="form-control form-control-sm" placeholder="Optional remarks...">
                            </td>
                        `;
                        studentTableBody.appendChild(tr);
                    });

                    studentListContainer.classList.remove('d-none');
                })
                .catch(err => console.error('Error fetching students:', err));
        });
    }

    // 3. Mark All Present / Absent Toggles
    if (btnMarkAllPresent) {
        btnMarkAllPresent.addEventListener('click', function() {
            const presentInputs = document.querySelectorAll('input[value="Present"]');
            presentInputs.forEach(input => input.checked = true);
        });
    }

    if (btnMarkAllAbsent) {
        btnMarkAllAbsent.addEventListener('click', function() {
            const absentInputs = document.querySelectorAll('input[value="Absent"]');
            absentInputs.forEach(input => input.checked = true);
        });
    }
});
