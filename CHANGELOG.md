# Changelog - Sistema Palpiteiros

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.0.0] - 2026-03-17
### Adicionado (Added)
- **Nova Sala de Troféus:** Galeria de Lendas com cards interativos no estilo "Ultimate Team".
- **Sistema de Troféus Reais:** Prateleiras VIP exibindo imagens reais das taças conquistadas (Brasileirão, Copa do Brasil, Libertadores, etc).
- **Contador de Títulos:** Badge automático que conta quantos títulos o jogador tem na carreira.
- **Gestão de Jogos Adiados:** Novo painel no Admin para gerenciar partidas sem data definida, permitindo reativá-las no futuro.
- **Status "Adiado":** Etiqueta visual vermelha e chamativa nos cards de jogos na página inicial quando uma partida é adiada.
- **Controle de Palpite Campeão:** Botão no painel Admin para abrir ou fechar a janela de palpites do campeão.
- **Ambiente Local Inteligente:** Script `run_local.py` para rodar o site e a API simultaneamente sem precisar alterar URLs no código.
- **Temporada Dinâmica:** Ano e temporada agora atualizam automaticamente em todo o site via painel.
- **Link de Feedback:** Botão nas regras direcionando para as Issues do GitHub para reporte de bugs e sugestões.

### Modificado (Changed)
- Melhoria no contraste e legibilidade das estatísticas (Pontos, Acertos, Erros) dentro da Sala de Troféus.
- Formulário de resultados no painel Admin agora permite salvar um jogo sem placar caso o status seja "Adiado".
- Atualização visual dos alertas (Anúncios) da página inicial.

### Corrigido (Fixed)
- Correção do bug onde o botão de "Fazer Palpite de Campeão" desaparecia para os demais usuários assim que o primeiro palpite era registrado.
---
## [0.0.9] - 2024-11-15 até 2026-03-16
### Adicionado (Added)
- **Arquitetura em Nuvem:** Separação do ecossistema no PythonAnywhere (conta independente para a API e outra para o Frontend/Backend).
- **Sincronização Automática:** Criação de scripts em Python (`update_games_brasi.py`, `copa.py`, `libert.py`) para atualizar os dados dos jogos de forma automatizada na base de dados local.
- **Motor de Pontuação:** Lógica base finalizada para cálculo de pontos (acerto do resultado exato, acerto apenas do vencedor/empate, e quem avança na fase a eliminar/mata-mata).
- **Bónus de Sequência:** Implementação do sistema de *streaks*, que atribui pontos extra aos utilizadores que mantêm uma sequência de bons palpites.
- **Painel de Administração (V1):** Interface dedicada para o moderador inserir os resultados reais dos jogos e definir o campeão do torneio.
- **Galeria de Campeões (V1):** Primeira versão da página de histórico, listando as conquistas dos utilizadores num formato de tabela simples.

### Modificado (Changed)
- Otimização das chamadas à base de dados `api_data.db` para reduzir o tempo de carregamento no ecrã principal.
- Ajustes na estrutura das tabelas para suportar múltiplos campeonatos em simultâneo (Brasileirão, Copa do Brasil e Libertadores).
### Adicionado (Added)
- **Arquitetura em Nuvem:** Separação do ecossistema no PythonAnywhere (conta independente para a API e outra para o Frontend/Backend).
- **Sincronização Automática:** Criação de scripts em Python (`update_games_brasi.py`, `copa.py`, `libert.py`) para atualizar os dados dos jogos de forma automatizada na base de dados local.
- **Motor de Pontuação:** Lógica base finalizada para cálculo de pontos (acerto do resultado exato, acerto apenas do vencedor/empate, e quem avança na fase a eliminar/mata-mata).
- **Bónus de Sequência:** Implementação do sistema de *streaks*, que atribui pontos extra aos utilizadores que mantêm uma sequência de bons palpites.
- **Painel de Administração (V1):** Interface dedicada para o moderador inserir os resultados reais dos jogos e definir o campeão do torneio.
- **Galeria de Campeões (V1):** Primeira versão da página de histórico, listando as conquistas dos utilizadores num formato de tabela simples.

### Modificado (Changed)
- Otimização das chamadas à base de dados `api_data.db` para reduzir o tempo de carregamento no ecrã principal.
- Ajustes na estrutura das tabelas para suportar múltiplos campeonatos em simultâneo (Brasileirão, Copa do Brasil e Libertadores).
