// 全局配置
const API_BASE = '';
let isLoading = false;
let charts = {};

// ==================== 工具函数 ====================

function showMessage(elementId, message, type='success') {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    el.style.display = 'block';
    el.className = 'message message-' + type;
    el.textContent = message;
    
    setTimeout(function() {
        el.style.display = 'none';
    }, 3000);
}

function showLoading(buttonEl, text) {
    text = text || '处理中...';
    if (buttonEl) {
        buttonEl.disabled = true;
        buttonEl.dataset.originalText = buttonEl.textContent;
        buttonEl.textContent = text;
    }
    isLoading = true;
}

function hideLoading(buttonEl) {
    if (buttonEl && buttonEl.dataset.originalText) {
        buttonEl.disabled = false;
        buttonEl.textContent = buttonEl.dataset.originalText;
    }
    isLoading = false;
}

function getStatusBadge(status) {
    const classMap = {
        'available': 'status-available',
        'in_use': 'status-in-use',
        'pending': 'status-pending',
        'assigned': 'status-assigned',
        'completed': 'status-completed'
    };
    const className = classMap[status] || 'status-pending';
    return '<span class="status-badge ' + className + '">' + status + '</span>';
}

// ==================== 仪表盘 ====================

function loadDashboard() {
    fetch(API_BASE + '/api/stats')
    .then(function(res) {
        return res.json();
    })
    .then(function(stats) {
        const todayEl = document.getElementById('today-requests');
        const completionEl = document.getElementById('completion-rate');
        const utilizationEl = document.getElementById('utilization-rate');
        const availableEl = document.getElementById('available-vehicles');
        
        if (todayEl) animateNumber(todayEl, stats.today_requests);
        if (completionEl) animateNumber(completionEl, stats.completion_rate, '%');
        if (utilizationEl) animateNumber(utilizationEl, stats.utilization_rate, '%');
        if (availableEl) animateNumber(availableEl, stats.available_vehicles);
        
        // 加载图表
        loadCharts();
    })
    .catch(function(error) {
        console.error('Failed to load dashboard:', error);
    });
}

function animateNumber(element, targetValue, suffix) {
    suffix = suffix || '';
    const startValue = parseInt(element.textContent) || 0;
    const duration = 500;
    const startTime = Date.now();
    
    function update() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentValue = Math.round(startValue + (targetValue - startValue) * progress);
        
        element.textContent = currentValue + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function loadVehicleReturnTimes() {
    fetch(API_BASE + '/api/vehicles')
    .then(function(res) {
        return res.json();
    })
    .then(function(vehicles) {
        const tbody = document.getElementById('return-times-tbody');
        if (!tbody) return;
        
        const inUseVehicles = vehicles.filter(function(v) {
            return v.status === 'in_use';
        });
        
        if (inUseVehicles.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty-text">All vehicles available</td></tr>';
            return;
        }
        
        let html = '';
        for (let i = 0; i < inUseVehicles.length; i++) {
            const v = inUseVehicles[i];
            html += '<tr>';
            html += '<td><strong>' + v.id + '</strong></td>';
            html += '<td>' + v.type + '</td>';
            html += '<td>' + getStatusBadge(v.status) + '</td>';
            html += '<td>' + (v.last_return_time || 'Unknown') + '</td>';
            html += '<td>';
            html += '<button onclick="verifyReturn(\'' + v.id + '\')" class="btn btn-success btn-small">Confirm Return</button>';
            html += '</td>';
            html += '</tr>';
        }
        
        tbody.innerHTML = html;
    })
    .catch(function(error) {
        console.error('Failed to load vehicle return times:', error);
    });
}

function verifyReturn(vehicleId) {
    if (!confirm('Confirm return for vehicle ' + vehicleId + '?')) {
        return;
    }
    
    fetch(API_BASE + '/api/vehicles/' + vehicleId + '/return', {
        method: 'POST'
    })
    .then(function(res) {
        return res.json();
    })
    .then(function(result) {
        if (result.success) {
            showMessage('dashboard-message', 'Vehicle return verified!', 'success');
            loadDashboard();
            loadVehicleReturnTimes();
        } else {
            showMessage('dashboard-message', 'Failed: ' + result.message, 'error');
        }
    })
    .catch(function(error) {
        showMessage('dashboard-message', 'Error: ' + error.message, 'error');
    });
}

// ==================== 图表 ====================

function loadCharts() {
    fetch(API_BASE + '/api/stats/detailed')
    .then(function(res) {
        return res.json();
    })
    .then(function(stats) {
        renderCharts(stats);
    })
    .catch(function(error) {
        console.error('Failed to load charts:', error);
    });
}

function renderCharts(stats) {
    // 车辆类型分布（饼图）
    if (charts.vehicleType) charts.vehicleType.destroy();
    const vehicleTypeCtx = document.getElementById('vehicle-type-chart').getContext('2d');
    charts.vehicleType = new Chart(vehicleTypeCtx, {
        type: 'pie',
        data: {
            labels: stats.vehicle_types.map(function(v) { return v.type; }),
            datasets: [{
                data: stats.vehicle_types.map(function(v) { return v.count; }),
                backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#48bb78', '#ed8936']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
    
    // 申请状态（环形图）
    if (charts.requestStatus) charts.requestStatus.destroy();
    const requestStatusCtx = document.getElementById('request-status-chart').getContext('2d');
    charts.requestStatus = new Chart(requestStatusCtx, {
        type: 'doughnut',
        data: {
            labels: stats.request_status.map(function(v) { return v.status; }),
            datasets: [{
                data: stats.request_status.map(function(v) { return v.count; }),
                backgroundColor: ['#48bb78', '#bee3f8', '#fed7d7']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
    
    // 车辆状态（柱状图）
    if (charts.vehicleStatus) charts.vehicleStatus.destroy();
    const vehicleStatusCtx = document.getElementById('vehicle-status-chart').getContext('2d');
    charts.vehicleStatus = new Chart(vehicleStatusCtx, {
        type: 'bar',
        data: {
            labels: stats.vehicle_status.map(function(v) { return v.status; }),
            datasets: [{
                label: 'Vehicle Count',
                data: stats.vehicle_status.map(function(v) { return v.count; }),
                backgroundColor: ['#48bb78', '#feebc8']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            }
        }
    });
    
    // 每日申请趋势（折线图）
    if (charts.dailyRequests) charts.dailyRequests.destroy();
    const dailyRequestsCtx = document.getElementById('daily-requests-chart').getContext('2d');
    charts.dailyRequests = new Chart(dailyRequestsCtx, {
        type: 'line',
        data: {
            labels: stats.daily_requests.map(function(v) { return v.date; }),
            datasets: [{
                label: 'Requests',
                data: stats.daily_requests.map(function(v) { return v.count; }),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// ==================== 车辆管理 ====================

function loadVehicles() {
    fetch(API_BASE + '/api/vehicles')
    .then(function(res) {
        return res.json();
    })
    .then(function(vehicles) {
        const tbody = document.getElementById('vehicles-tbody');
        if (!tbody) return;
        
        if (vehicles.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-text">No vehicles yet</td></tr>';
            return;
        }
        
        let html = '';
        for (let i = 0; i < vehicles.length; i++) {
            const v = vehicles[i];
            html += '<tr>';
            html += '<td><strong>' + v.id + '</strong></td>';
            html += '<td>' + v.type + '</td>';
            html += '<td>' + v.capacity + ' people</td>';
            html += '<td>' + getStatusBadge(v.status) + '</td>';
            html += '<td>' + (v.last_return_time || '-') + '</td>';
            html += '<td>';
            html += '<button onclick="deleteVehicle(\'' + v.id + '\')" class="btn btn-danger btn-small">Delete</button>';
            html += '</td>';
            html += '</tr>';
        }
        
        tbody.innerHTML = html;
    })
    .catch(function(error) {
        console.error('Failed to load vehicles:', error);
    });
}

function addVehicle() {
    if (isLoading) return;
    
    const btn = event ? event.submitter : null;
    if (!btn) btn = document.querySelector('#vehicle-form button[type="submit"]');
    showLoading(btn, 'Adding...');
    
    const id = document.getElementById('vehicle-id').value.trim();
    const type = document.getElementById('vehicle-type').value;
    const capacity = document.getElementById('vehicle-capacity').value;
    
    if (!id || !type || !capacity) {
        showMessage('vehicle-message', 'Please fill all fields', 'error');
        hideLoading(btn);
        return;
    }
    
    fetch(API_BASE + '/api/vehicles', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            id: id,
            type: type,
            capacity: parseInt(capacity)
        })
    })
    .then(function(res) {
        return res.json();
    })
    .then(function(result) {
        if (result.success) {
            showMessage('vehicle-message', result.message, 'success');
            document.getElementById('vehicle-form').reset();
            loadVehicles();
            loadDashboard();
        } else {
            showMessage('vehicle-message', result.message, 'error');
        }
    })
    .catch(function(error) {
        showMessage('vehicle-message', 'Failed: ' + error.message, 'error');
    })
    .finally(function() {
        hideLoading(btn);
    });
}

function deleteVehicle(vehicleId) {
    if (isLoading) return;
    
    if (!confirm('Delete vehicle ' + vehicleId + '?')) {
        return;
    }
    
    fetch(API_BASE + '/api/vehicles/' + vehicleId, {
        method: 'DELETE'
    })
    .then(function(res) {
        return res.json();
    })
    .then(function(result) {
        showMessage('vehicle-message', result.message, 'success');
        loadVehicles();
        loadDashboard();
    })
    .catch(function(error) {
        showMessage('vehicle-message', 'Failed: ' + error.message, 'error');
    });
}

// ==================== 用车申请 ====================

function loadRequests() {
    fetch(API_BASE + '/api/requests')
    .then(function(res) {
        return res.json();
    })
    .then(function(requests) {
        const tbody = document.getElementById('requests-tbody');
        if (!tbody) return;
        
        if (requests.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-text">No requests yet</td></tr>';
            return;
        }
        
        let html = '';
        for (let i = 0; i < requests.length; i++) {
            const r = requests[i];
            html += '<tr>';
            html += '<td><strong>' + r.requester_name + '</strong></td>';
            html += '<td>' + r.start_location + ' → ' + r.end_location + '</td>';
            html += '<td>' + r.passengers + ' people</td>';
            html += '<td>' + r.request_time + '</td>';
            html += '<td>' + getStatusBadge(r.status) + '</td>';
            html += '<td>';
            html += '<button onclick="deleteRequest(' + r.id + ')" class="btn btn-danger btn-small">Delete</button>';
            html += '</td>';
            html += '</tr>';
        }
        
        tbody.innerHTML = html;
    })
    .catch(function(error) {
        console.error('Failed to load requests:', error);
    });
}

function addRequest() {
    if (isLoading) return;
    
    const btn = event ? event.submitter : null;
    if (!btn) btn = document.querySelector('#request-form button[type="submit"]');
    showLoading(btn, 'Submitting...');
    
    const requester = document.getElementById('requester').value.trim();
    const startLocation = document.getElementById('start-location').value.trim();
    const endLocation = document.getElementById('end-location').value.trim();
    const passengers = document.getElementById('passengers').value;
    const requestTime = document.getElementById('request-time').value;
    const notes = document.getElementById('notes').value.trim();
    
    if (!requester || !startLocation || !endLocation || !passengers || !requestTime) {
        showMessage('request-message', 'Please fill required fields', 'error');
        hideLoading(btn);
        return;
    }
    
    fetch(API_BASE + '/api/requests', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            requester_name: requester,
            start_location: startLocation,
            end_location: endLocation,
            passengers: parseInt(passengers),
            request_time: requestTime,
            notes: notes
        })
    })
    .then(function(res) {
        return res.json();
    })
    .then(function(result) {
        if (result.success) {
            showMessage('request-message', result.message, 'success');
            document.getElementById('request-form').reset();
            document.getElementById('request-time').value = new Date().toISOString().slice(0, 16);
            loadRequests();
            loadDashboard();
        } else {
            showMessage('request-message', result.message, 'error');
        }
    })
    .catch(function(error) {
        showMessage('request-message', 'Failed: ' + error.message, 'error');
    })
    .finally(function() {
        hideLoading(btn);
    });
}

function deleteRequest(requestId) {
    if (isLoading) return;
    
    if (!confirm('Delete request #' + requestId + '?')) {
        return;
    }
    
    fetch(API_BASE + '/api/requests/' + requestId, {
        method: 'DELETE'
    })
    .then(function(res) {
        return res.json();
    })
    .then(function(result) {
        showMessage('request-message', result.message, 'success');
        loadRequests();
        loadDashboard();
    })
    .catch(function(error) {
        showMessage('request-message', 'Failed: ' + error.message, 'error');
    });
}

// ==================== 智能调度 ====================

function runSchedule() {
    if (isLoading) return;
    
    const btn = event ? event.target : null;
    if (!btn) btn = document.querySelector('button[onclick="runSchedule()"]');
    showLoading(btn, 'Scheduling...');
    
    const messageEl = document.getElementById('schedule-message');
    if (messageEl) messageEl.style.display = 'none';
    
    fetch(API_BASE + '/api/schedule', {
        method: 'POST'
    })
    .then(function(res) {
        return res.json();
    })
    .then(function(result) {
        if (result.success) {
            showMessage('schedule-message', 'Schedule completed!', 'success');
            loadScheduleResult();
            loadDashboard();
        } else {
            showMessage('schedule-message', 'Failed: ' + result.message, 'error');
        }
    })
    .catch(function(error) {
        showMessage('schedule-message', 'Failed: ' + error.message, 'error');
    })
    .finally(function() {
        hideLoading(btn);
    });
}

function loadScheduleResult() {
    fetch(API_BASE + '/api/schedule/result')
    .then(function(res) {
        return res.json();
    })
    .then(function(result) {
        const container = document.getElementById('schedule-result');
        if (!container) return;
        
        if (!result || result.length === 0) {
            container.innerHTML = '<p class="empty-text">No schedule result. Click "Run Schedule" to start.</p>';
            return;
        }
        
        let html = '';
        for (let i = 0; i < result.length; i++) {
            const group = result[i];
            html += '<div class="schedule-card">';
            html += '<h3>🚗 ' + group.vehicle_id + ' (' + group.vehicle_type + ', Capacity: ' + group.vehicle_capacity + ')</h3>';
            
            for (let j = 0; j < group.tasks.length; j++) {
                const task = group.tasks[j];
                html += '<div class="task-item">';
                html += '<strong>' + task.requester + '</strong><br>';
                html += '📍 ' + task.start_location + ' → ' + task.end_location + '<br>';
                html += '👥 ' + task.passengers + ' people | 🕐 ' + task.request_time;
                html += '</div>';
            }
            
            html += '</div>';
        }
        
        container.innerHTML = html;
    })
    .catch(function(error) {
        console.error('Failed to load schedule result:', error);
    });
}

function resetSchedule() {
    if (isLoading) return;
    
    if (!confirm('Reset schedule? This will release all vehicles and reset request status.')) {
        return;
    }
    
    const btn = event ? event.target : null;
    if (!btn) btn = document.querySelector('button[onclick="resetSchedule()"]');
    showLoading(btn, 'Resetting...');
    
    fetch(API_BASE + '/api/schedule/reset', {
        method: 'POST'
    })
    .then(function(res) {
        return res.json();
    })
    .then(function(result) {
        showMessage('schedule-message', result.message, result.success ? 'success' : 'error');
        if (result.success) {
            loadScheduleResult();
            loadDashboard();
        }
    })
    .catch(function(error) {
        showMessage('schedule-message', 'Failed: ' + error.message, 'error');
    })
    .finally(function() {
        hideLoading(btn);
    });
}

// ==================== 页面初始化 ====================

document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    
    if (path === '/' || path === '/index') {
        loadDashboard();
        loadVehicleReturnTimes();
        
        // 自动刷新（每30秒）
        setInterval(function() {
            loadDashboard();
            loadVehicleReturnTimes();
        }, 30000);
    } else if (path === '/vehicles') {
        loadVehicles();
        
        // 自动刷新（每15秒）
        setInterval(function() {
            loadVehicles();
        }, 15000);
    } else if (path === '/requests') {
        loadRequests();
        
        // 自动刷新（每15秒）
        setInterval(function() {
            loadRequests();
        }, 15000);
    } else if (path === '/schedule') {
        loadScheduleResult();
        
        // 自动刷新（每20秒）
        setInterval(function() {
            loadScheduleResult();
        }, 20000);
    }
});
