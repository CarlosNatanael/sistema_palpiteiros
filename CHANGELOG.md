# Changelog - Sistema Palpiteiros

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.0.0] - 2026-03-17
### 🚀 Adicionado (Added)
- **Nova Sala de Troféus:** Galeria de Lendas com cards interativos no estilo "Ultimate Team".
- **Sistema de Troféus Reais:** Prateleiras VIP exibindo imagens reais das taças conquistadas (Brasileirão, Copa do Brasil, Libertadores, etc).
- **Contador de Títulos:** Badge automático que conta quantos títulos o jogador tem na carreira.
- **Gestão de Jogos Adiados:** Novo painel no Admin para gerenciar partidas sem data definida, permitindo reativá-las no futuro.
- **Status "Adiado":** Etiqueta visual vermelha e chamativa nos cards de jogos na página inicial quando uma partida é adiada.
- **Controle de Palpite Campeão:** Botão no painel Admin para abrir ou fechar a janela de palpites do campeão.
- **Ambiente Local Inteligente:** Script `run_local.py` para rodar o site e a API simultaneamente sem precisar alterar URLs no código.
- **Temporada Dinâmica:** Ano e temporada agora atualizam automaticamente em todo o site via painel.
- **Link de Feedback:** Botão nas regras direcionando para as Issues do GitHub para reporte de bugs e sugestões.

### 🔄 Modificado (Changed)
- Melhoria no contraste e legibilidade das estatísticas (Pontos, Acertos, Erros) dentro da Sala de Troféus.
- Formulário de resultados no painel Admin agora permite salvar um jogo sem placar caso o status seja "Adiado".
- Atualização visual dos alertas (Anúncios) da página inicial.

### 🐛 Corrigido (Fixed)
- Correção do bug onde o botão de "Fazer Palpite de Campeão" desaparecia para os demais usuários assim que o primeiro palpite era registrado.