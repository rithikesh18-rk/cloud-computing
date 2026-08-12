// Reports & Analytics Chart JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const reportTypeSelect = document.getElementById('report_type_select');
    const filterDept = document.getElementById('filter_dept_group');
    const filterSubj = document.getElementById('filter_subj_group');
    const filterStudent = document.getElementById('filter_student_group');
    const filterDateRange = document.getElementById('filter_date_group');

    function updateFilterVisibility() {
        if (!reportTypeSelect) return;
        const val = reportTypeSelect.value;

        // Hide all optional filters by default
        if (filterDept) filterDept.classList.add('d-none');
        if (filterSubj) filterSubj.classList.add('d-none');
        if (filterStudent) filterStudent.classList.add('d-none');
        if (filterDateRange) filterDateRange.classList.add('d-none');

        if (val === 'daily') {
            if (filterDept) filterDept.classList.remove('d-none');
            if (filterDateRange) filterDateRange.classList.remove('d-none');
        } else if (val === 'weekly' || val === 'monthly') {
            if (filterDept) filterDept.classList.remove('d-none');
            if (filterDateRange) filterDateRange.classList.remove('d-none');
        } else if (val === 'student') {
            if (filterStudent) filterStudent.classList.remove('d-none');
        } else if (val === 'subject') {
            if (filterSubj) filterSubj.classList.remove('d-none');
        } else if (val === 'department') {
            if (filterDept) filterDept.classList.remove('d-none');
        }
    }

    if (reportTypeSelect) {
        reportTypeSelect.addEventListener('change', updateFilterVisibility);
        updateFilterVisibility(); // Initial call
    }
});
