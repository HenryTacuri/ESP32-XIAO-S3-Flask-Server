const trackbarSal = document.getElementById('trackbarSal');
const valorTrackbarSal = document.getElementById('valorTrackbarSal');

const trackbarPimienta = document.getElementById('trackbarPimienta');
const valorTrackbarPimienta = document.getElementById('valorTrackbarPimienta');

trackbarSal.addEventListener('input', function() {
    valorTrackbarSal.textContent = trackbarSal.value; 
    enviarValores(); 
});

trackbarPimienta.addEventListener('input', function() {
    valorTrackbarPimienta.textContent = trackbarPimienta.value; 
    enviarValores(); 
});


function enviarValores() {
    const valorSal = trackbarSal.value;
    const valorPimienta = trackbarPimienta.value;
    
    $.ajax({
        url: '/get_sal_pimienta',  
        method: 'POST',         
        data: { 
            trackbarSal: valorSal,
            trackbarPimienta: valorPimienta
        }
    });
}