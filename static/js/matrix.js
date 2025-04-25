// Efeito Matrix para o site Gerador de Jogos da Lotofácil

// Inicialização do canvas quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Criar elemento canvas
    const canvas = document.createElement('canvas');
    canvas.id = 'matrix-canvas';
    document.body.insertBefore(canvas, document.body.firstChild);
    
    // Configurar o canvas
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // Caracteres para o efeito Matrix
    const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    
    // Tamanho da fonte
    const fontSize = 14;
    
    // Calcular número de colunas
    const columns = Math.floor(canvas.width / fontSize);
    
    // Array para posição Y de cada coluna
    const drops = [];
    
    // Inicializar todas as posições Y
    for (let i = 0; i < columns; i++) {
        drops[i] = Math.random() * -100;
    }
    
    // Função para desenhar o efeito Matrix
    function draw() {
        // Fundo semi-transparente para criar efeito de rastro
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Cor e fonte para os caracteres
        ctx.fillStyle = '#33ff33';
        ctx.font = fontSize + 'px monospace';
        
        // Loop através de cada coluna
        for (let i = 0; i < drops.length; i++) {
            // Escolher um caractere aleatório
            const text = chars[Math.floor(Math.random() * chars.length)];
            
            // Desenhar o caractere
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            
            // Reiniciar a posição Y quando atingir o fundo ou aleatoriamente
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            
            // Mover para baixo
            drops[i]++;
        }
    }
    
    // Redimensionar canvas quando a janela for redimensionada
    window.addEventListener('resize', function() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        // Recalcular número de colunas
        const newColumns = Math.floor(canvas.width / fontSize);
        
        // Ajustar array de posições Y
        if (newColumns > columns) {
            // Adicionar novas colunas
            for (let i = columns; i < newColumns; i++) {
                drops[i] = Math.random() * -100;
            }
        }
    });
    
    // Iniciar animação
    setInterval(draw, 35);
});

// Funções para interatividade da página

// Alternar entre planos
function togglePlanDetails(planId) {
    const planDetails = document.getElementById(planId);
    if (planDetails.style.display === 'none') {
        planDetails.style.display = 'block';
    } else {
        planDetails.style.display = 'none';
    }
}

// Simulação de progresso para treinamento da IA
function simulateTraining() {
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.querySelector('.progress-text');
    let progress = 0;
    
    // Desabilitar botão durante o treinamento
    const trainButton = document.getElementById('train-button');
    if (trainButton) {
        trainButton.disabled = true;
        trainButton.textContent = 'Treinando...';
    }
    
    // Atualizar a barra de progresso
    const interval = setInterval(function() {
        progress += Math.random() * 2;
        if (progress > 100) {
            progress = 100;
            clearInterval(interval);
            
            // Reativar botão após o treinamento
            if (trainButton) {
                trainButton.disabled = false;
                trainButton.textContent = 'Iniciar Treinamento';
            }
            
            // Exibir mensagem de conclusão
            alert('Treinamento da IA concluído com sucesso!');
        }
        
        progressBar.style.width = progress + '%';
        progressText.textContent = Math.floor(progress) + '%';
    }, 200);
}

// Gerar jogos aleatórios para demonstração
function generateDemoGames() {
    const gamesContainer = document.getElementById('generated-games');
    if (!gamesContainer) return;
    
    // Limpar jogos anteriores
    gamesContainer.innerHTML = '';
    
    // Número de jogos a serem gerados
    const numGames = 5;
    
    for (let i = 0; i < numGames; i++) {
        // Criar um novo jogo
        const gameDiv = document.createElement('div');
        gameDiv.className = 'generated-game';
        
        // Gerar 15 números aleatórios entre 1 e 25
        const numbers = [];
        while (numbers.length < 15) {
            const num = Math.floor(Math.random() * 25) + 1;
            if (!numbers.includes(num)) {
                numbers.push(num);
            }
        }
        
        // Ordenar os números
        numbers.sort((a, b) => a - b);
        
        // Criar bolas de loteria para cada número
        for (let j = 0; j < numbers.length; j++) {
            const ball = document.createElement('div');
            ball.className = 'lottery-ball';
            ball.textContent = numbers[j];
            gameDiv.appendChild(ball);
        }
        
        // Adicionar o jogo ao container
        gamesContainer.appendChild(gameDiv);
    }
}

// Simular verificação de pagamento
function checkPaymentStatus() {
    // Simulação de verificação de pagamento
    const statusElement = document.getElementById('payment-status');
    if (!statusElement) return;
    
    statusElement.textContent = 'Verificando pagamento...';
    
    // Simular tempo de processamento
    setTimeout(function() {
        // Simulação de resultado aleatório (para demonstração)
        const isPaid = Math.random() > 0.5;
        
        if (isPaid) {
            statusElement.textContent = 'Pagamento confirmado! Redirecionando...';
            statusElement.style.color = '#33ff33';
            
            // Redirecionar após confirmação
            setTimeout(function() {
                window.location.href = 'dashboard.html';
            }, 2000);
        } else {
            statusElement.textContent = 'Pagamento pendente. Tente novamente em alguns instantes.';
            statusElement.style.color = '#ff3333';
        }
    }, 2000);
}

// Implementar ciclo de dezenas fora (para assinantes premium)
function analyzeCycle() {
    const cycleContainer = document.getElementById('cycle-analysis');
    if (!cycleContainer) return;
    
    // Limpar análise anterior
    cycleContainer.innerHTML = '<h3>Análise de Ciclo de Dezenas Fora</h3>';
    
    // Criar tabela para mostrar o ciclo
    const table = document.createElement('table');
    table.className = 'results-table';
    
    // Cabeçalho da tabela
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    const headers = ['Dezena', 'Status', 'Concursos Fora', 'Probabilidade'];
    headers.forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Corpo da tabela
    const tbody = document.createElement('tbody');
    
    // Simular 10 dezenas para o ciclo
    const outNumbers = [2, 5, 9, 13, 16, 17, 19, 21, 23, 25];
    
    outNumbers.forEach(num => {
        const row = document.createElement('tr');
        
        // Dezena
        const numCell = document.createElement('td');
        numCell.textContent = num;
        row.appendChild(numCell);
        
        // Status (aleatório para demonstração)
        const statusCell = document.createElement('td');
        const isOut = Math.random() > 0.5;
        statusCell.textContent = isOut ? 'Fora' : 'Sorteada';
        statusCell.style.color = isOut ? '#33ff33' : '#ff3333';
        row.appendChild(statusCell);
        
        // Concursos fora
        const concursosCell = document.createElement('td');
        concursosCell.textContent = Math.floor(Math.random() * 10) + 1;
        row.appendChild(concursosCell);
        
        // Probabilidade
        const probCell = document.createElement('td');
        probCell.textContent = (Math.random() * 30 + 70).toFixed(2) + '%';
        row.appendChild(probCell);
        
        tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    cycleContainer.appendChild(table);
    
    // Adicionar resumo do ciclo
    const summary = document.createElement('div');
    summary.className = 'cycle-summary';
    summary.innerHTML = `
        <p>Status do ciclo: <strong>Em andamento</strong></p>
        <p>Dezenas já sorteadas: <strong>${Math.floor(Math.random() * 6) + 4}/10</strong></p>
        <p>Estimativa para fechamento do ciclo: <strong>${Math.floor(Math.random() * 3) + 1} concursos</strong></p>
    `;
    
    cycleContainer.appendChild(summary);
}
