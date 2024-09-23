const apiBaseUrl = 'http://localhost:5242/api/Students';
const errorBaseUrl = 'http://localhost:5242/api/Error';
const errorContainer = document.getElementById('error-container');
const studentsTableBody = document.querySelector('#students-table tbody');

async function getStudents() {
    try {
        const limit = document.querySelector('#limit').value;
        const offset = document.querySelector('#offset').value;
        const response = await fetch(`${apiBaseUrl}?limit=${+limit || 10}&offset=${+offset || 0}`);
        if (!response.ok) {
            handleError(response);
            return;
        }
        const students = await response.json();
        renderStudents(students);
    } catch (error) {
        showError('Failed to fetch students: ' + error.message);
    }
}

function renderStudents(students) {
    studentsTableBody.innerHTML = '';
    students.forEach(student => {
        const row = `<tr>
            <td>${student.id}</td>
            <td>${student.name}</td>
            <td>${student.phone}</td>
        </tr>`;
        studentsTableBody.insertAdjacentHTML('beforeend', row);
    });
}

document.getElementById('add-student-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const phone = document.getElementById('phone').value;

    try {
        const response = await fetch(apiBaseUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: 0, name, phone })
        });
        if (!response.ok) {
            handleError(response);
            return;
        }
        getStudents();
    } catch (error) {
        showError('Failed to add student: ' + error.message);
    }
});

document.getElementById('edit-student-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const id = document.getElementById('edit-id').value;
    const name = document.getElementById('edit-name').value;
    const phone = document.getElementById('edit-phone').value;

    try {
        const response = await fetch(`${apiBaseUrl}/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, name, phone })
        });
        if (!response.ok) {
            handleError(response);
            return;
        }
        getStudents();
    } catch (error) {
        showError('Failed to update student: ' + error.message);
    }
});

document.getElementById('delete-student-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const id = document.getElementById('delete-id').value;

    try {
        const response = await fetch(`${apiBaseUrl}/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            handleError(response);
            return;
        }
        getStudents();
    } catch (error) {
        showError('Failed to delete student: ' + error.message);
    }
});

async function handleError(response) {
    const errorResponse = await response.json();
    const errorId = errorResponse.hateos;
    try {
        const errorDetailsResponse = await fetch(`${errorBaseUrl}/${errorId}`);
        const errorDetails = await errorDetailsResponse.json();
        showError(`Error ${errorId}: ${errorDetails.detail}`);
    } catch (e) {
        showError('Failed to retrieve error details.');
    }
}

function showError(message) {
    errorContainer.innerHTML = `<div class="error">${message}</div>`;
}

