\# 📘 Manual do Usuário - Automação de Bandas FT8 (PP5EO)



\*\*Autor:\*\* MUNIZ, Renato de Souza - PP5EO

\*\*Versão:\*\* 1.0.0



Este manual descreve o funcionamento, configuração e operação do sistema de automação de bandas para radioamadores.



---



\## 1. Visão Geral

O software atua como um "maestro" entre o seu software de decodificação (WSJT-X ou JTDX) e o seu rádio (via FLRIG).



\* \*\*Objetivo:\*\* Permitir que a estação monitore múltiplas bandas automaticamente, trocando de frequência em intervalos regulares, mas respeitando momentos de transmissão (QSO) para não interromper contatos.

\* \*\*Arquitetura:\*\* \* Lê tráfego UDP na porta 2237 (Multicast ou Localhost).

&nbsp;   \* Envia comandos XML-RPC para o FLRIG.



---



\## 2. Interface Principal



\### A. Cabeçalho (Status)

\* \*\*FLRIG:\*\* Indica se a conexão com o rádio está ativa (Verde = OK, Vermelho = Erro).

\* \*\*WSJT/JTDX:\*\* Indica se há pacotes sendo recebidos do software de FT8 (Verde = Recebendo, Laranja = Aguardando).

\* \*\*PRÓXIMA TROCA:\*\* Um contador regressivo mostrando quanto tempo falta para mudar para a próxima banda.

\* \*\*Botões de Controle:\*\*

&nbsp;   \* `⚙ CONFIG`: Abre a janela de configurações técnicas.

&nbsp;   \* `ℹ SOBRE`: Exibe créditos e licença.

&nbsp;   \* `🔊 SOM ON/MUDO`: Liga ou desliga os bipes de alerta de DX.

&nbsp;   \* `PAUSAR`: Interrompe o temporizador. O software continua monitorando, mas não troca mais de banda.



\### B. Tabela de Alertas

Lista os últimos indicativos recebidos que coincidem com sua \*\*Watchlist\*\* ou chamadas de CQ, dependendo da configuração.

\* \*\*Cores:\*\* As linhas alternam de cor a cada 2.5 segundos para indicar visualmente que o sistema está "vivo" e recebendo dados.



\### C. Configuração de Bandas (Painel Expansível)

Aqui você define a estratégia de monitoramento.

\* \*\*Coluna Banda:\*\* O nome da banda (ex: 10m, 20m). Um \*\*Duplo Clique\*\* força a ida imediata para essa banda.

\* \*\*Coluna ☀ Dia:\*\* Marque para incluir esta banda no ciclo de monitoramento diurno (ex: bandas altas como 10m, 12m, 15m).

\* \*\*Coluna 🌙 Noite:\*\* Marque para incluir esta banda no ciclo noturno (ex: 40m, 80m).

\* \*\*Coluna Indicativos:\*\* Digite os indicativos que você quer caçar nesta banda (ex: `K1ABC, JA1XYZ`). Se um desses aparecer, o software emitirá um alerta sonoro.



---



\## 3. Lógica de Funcionamento



\### Ciclo Dia vs. Noite

O sistema verifica automaticamente o horário do computador.

\* Se estiver dentro do horário definido como "Dia" (ex: 07:00 às 18:30), ele rotaciona apenas entre as bandas marcadas na coluna \*\*☀ Dia\*\*.

\* Caso contrário, usa as bandas da coluna \*\*🌙 Noite\*\*.



\### Sistema de Segurança "Delay Pós-TX"

Esta é a função mais importante para evitar acidentes.

1\.  Se você apertar o PTT (transmitir) no rádio ou no WSJT-X, o sistema detecta imediatamente.

2\.  O cronômetro de troca de banda entra em modo \*\*HOLD\*\* (Espera).

3\.  Após você soltar o PTT, o sistema inicia uma contagem de segurança (padrão: 300 segundos / 5 minutos).

4\.  Durante esse tempo, \*\*nenhuma troca de banda automática ocorrerá\*\*. Isso garante que você consiga terminar seu QSO sem que o rádio mude de frequência no meio da conversa.

5\.  Aparecerá a mensagem `DELAY` em laranja no topo da tela.



---



\## 4. Configurações Avançadas (Botão ⚙ CONFIG)



\* \*\*Multicast/Local IP:\*\* Padrão `224.0.0.1` (Multicast) ou `127.0.0.1` (Local). Deve ser igual ao configurado no WSJT-X.

\* \*\*Porta:\*\* Padrão `2237`.

\* \*\*Intervalo de Troca:\*\* Quanto tempo o rádio fica em cada banda (1, 2, 5, 10 ou 15 min).

\* \*\*Início/Fim do Dia:\*\* Define o horário de transição entre propagação diurna e noturna.

\* \*\*Delay Pós-TX:\*\* Tempo de espera após uma transmissão antes de retomar a automação.



---



\## 5. Solução de Problemas



\*\*O FLRIG fica vermelho (OFF):\*\*

\* Verifique se o FLRIG está aberto.

\* Verifique se o XML-RPC está ativado no FLRIG (Config -> Setup -> Transceiver -> XML-RPC). A porta padrão é 12345.



\*\*O WSJT fica laranja (WAIT):\*\*

\* Verifique se o WSJT-X/JTDX está rodando.

\* Vá em \*File -> Settings -> Reporting\* e confirme se "UDP Server" está apontando para o IP e Porta corretos.



\*\*O rádio não muda de banda:\*\*

\* Verifique se o botão "PAUSAR" não está ativo.

\* Verifique se não está em modo "DELAY" (após uma transmissão).

