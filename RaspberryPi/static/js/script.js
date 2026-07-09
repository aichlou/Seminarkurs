const speedXSlider = document.getElementById('speedX');
const speedYSlider = document.getElementById('speedY');
const speedXValue = document.getElementById('speedXValue');
const speedYValue = document.getElementById('speedYValue');

speedXSlider.addEventListener('input', function() {
    speedXValue.textContent = this.value + '%';
});

speedYSlider.addEventListener('input', function() {
    speedYValue.textContent = this.value + '%';
});

let isClicked = { X: false, Y: false
};

function Clicked(axis) {
    console.log("Button " + axis + " clicked");
    isClicked[axis] = !isClicked[axis];
    if(isClicked[axis]) {
        activateMotor(axis);
    }
    else {
        deactivateMotor(axis);
    }
}

// Motor-Aktivierung
let motorStates = { X: false, Y: false};

function activateMotor(axis) {
    motorStates[axis] = true;
    const button = document.getElementById('action' + axis);
    button.classList.add('active');
    button.textContent = 'Motor ' + axis + ' Aktiv ●';
    
    const speed = document.getElementById('speed' + axis).value;
    
    fetch('/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            axis: axis,
            speed: parseInt(speed),
            active: true
        })
    });
}

function deactivateMotor(axis) {
    motorStates[axis] = false;
    const button = document.getElementById('action' + axis);
    button.classList.remove('active');
    button.textContent = 'Motor ' + axis + ' Aktivieren';
    
    fetch('/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            axis: axis,
            speed: 0,
            active: false
        })
    });
}

// Sensoren aktualisieren
function updateSensors() {
    fetch('/status')
        .then(r => r.json())
        .then(data => {
            const grid = document.getElementById('sensorsGrid');
            
            // Grid nur neu aufbauen wenn sich Anzahl ändert
            if (grid.children.length !== data.length) {
                grid.innerHTML = '';
                data.forEach((value, i) => {
                    const sensor = document.createElement('div');
                    sensor.id = 'sensor' + i;
                    sensor.className = 'sensor';
                    sensor.innerHTML = `
                        <div class="sensor-label">Sensor ${i + 1}</div>
                        <div class="sensor-value">?</div>
                    `;
                    grid.appendChild(sensor);
                });
            }
            
            // Werte aktualisieren
            data.forEach((value, i) => {
                const sensor = document.getElementById('sensor' + i);
                const valueEl = sensor.querySelector('.sensor-value');
                valueEl.textContent = value ? 'AN' : 'AUS';
                sensor.className = 'sensor ' + (value ? 'active' : 'inactive');
            });
        })
        .catch(err => console.error('Fehler beim Laden der Sensordaten:', err));
}

// Periodische Updates
setInterval(updateSensors, 1000);
updateSensors();

function init() {
    fetch('/init')
        .then(r => r.json())
        .then(data => {
            console.log(data);
        })
}