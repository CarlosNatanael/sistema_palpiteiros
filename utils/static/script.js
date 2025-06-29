// Configura a data de retorno (ano, mês-1, dia, hora, minuto)
const returnDate = new Date(2025, 5, 30, 10, 50).getTime();

function updateCountdown() {
    const now = new Date().getTime();
    const distance = returnDate - now;

    // Cálculos do tempo
    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Exibe o resultado
    document.getElementById("days").innerHTML = days.toString().padStart(2, '0');
    document.getElementById("hours").innerHTML = hours.toString().padStart(2, '0');
    document.getElementById("minutes").innerHTML = minutes.toString().padStart(2, '0');
    document.getElementById("seconds").innerHTML = seconds.toString().padStart(2, '0');

    // Se o contador terminar
    if (distance < 0) {
        clearInterval(countdownTimer);
        document.getElementById("countdown").innerHTML = "<p>Manutenção concluída! Atualize a página.</p>";
    }
}

// Atualiza a cada 1 segundo
const countdownTimer = setInterval(updateCountdown, 1000);
updateCountdown(); // Chamada inicial