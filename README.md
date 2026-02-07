# 📡 Automação de Bandas para WSJT-X / JTDX (Via FLRIG)

**Desenvolvido por: MUNIZ, Renato de Souza - PP5EO** *Licença: MIT (Código Aberto)*
**Repositório Oficial:** [github.com/renatoflp/ft8-band-automation](https://github.com/renatoflp/ft8-band-automation)

Este software é um utilitário de automação para radioamadores que operam modos digitais (FT8, FT4, etc.). Ele monitora o tráfego recebido pelo **WSJT-X** ou **JTDX** e gerencia a troca automática de bandas no rádio através do **FLRIG** baseado em horários e inatividade.

---

## ⚠️ ISENÇÃO DE RESPONSABILIDADE (DISCLAIMER)

**LEIA COM ATENÇÃO ANTES DE USAR:**

Este software é fornecido **"COMO ESTÁ" (AS IS)**, sem garantias de qualquer tipo, expressas ou implícitas.

1.  **Riscos ao Equipamento:** O autor **não se responsabiliza** por danos causados a transceptores, amplificadores, sintonizadores de antena ou computadores decorrentes do uso deste software. O controle automático de VFO (CAT) pode, em raras circunstâncias, causar comportamento inesperado no rádio.
2.  **Supervisão:** A automação não substitui o operador. É recomendável que o operador esteja presente durante o funcionamento para garantir a segurança da estação.
3.  **Conformidade Legal:** O software opera apenas em modo de **monitoramento (RX)** e controle de frequência. No entanto, é responsabilidade exclusiva do usuário garantir que sua estação opere dentro das normas da legislação local (ANATEL no Brasil, ou órgão equivalente em outros países).

**Ao utilizar este programa, você concorda que o está utilizando por sua própria conta e risco.**

---

## 🚀 Funcionalidades

* **Monitoramento Passivo:** Escuta o tráfego UDP local do WSJT-X/JTDX sem interferir na operação.
* **Troca Automática de Bandas:** Se passar um tempo (ex: 5 min) sem atividade ou contatos na banda atual, o software troca automaticamente para a próxima banda da lista.
* **Ciclo Dia / Noite:** Permite definir quais bandas usar durante o dia (ex: 10m, 15m, 20m) e durante a noite (ex: 40m, 80m).
* **Watchlist:** Alerta visual quando um indicativo de interesse é decodificado.
* **Integração FLRIG:** Compatível com qualquer rádio suportado pelo FLRIG (Icom, Yaesu, Kenwood, Xiegu, etc.).

---

## 🛠️ Pré-requisitos

1.  **Python 3.x** instalado.
2.  **FLRIG** instalado e configurado com seu rádio (CAT Control funcionando).
3.  **WSJT-X** ou **JTDX** instalado.

---

## ⚙️ Configuração Obrigatória

Para que o sistema funcione, você precisa configurar os softwares da seguinte forma:

### 1. No FLRIG
* Certifique-se de que o **XML-RPC** está ativado (padrão do FLRIG).
* O servidor deve estar rodando na porta `12345` (padrão).

### 2. No WSJT-X ou JTDX
O software precisa enviar os dados de decodificação para o nosso script.

* Vá em **File** -> **Settings** -> **Reporting**.
* Na seção **UDP Server**:
    * **UDP Server:** `127.0.0.1`
    * **UDP Server Port:** `2237`
    * Marque as opções:
        * ✅ **Accept UDP requests**
        * ✅ **Notify on accepted UDP request**
        * ✅ **Restore window on accepted UDP request**

---

## 📦 Como Instalar e Rodar

1.  Baixe ou clone este repositório.
2.  Instale o Python (se não tiver).
3.  Execute o arquivo principal:

    **Windows (Via terminal):**
    ```bash
    python main.py
    ```
    *(Ou apenas clique duas vezes no arquivo `main.py` se o Python estiver associado).*

4.  Uma janela abrirá.
    * Se o **FLRIG** estiver aberto, aparecerá "FLRIG ON".
    * Se o **WSJT/JTDX** estiver decodificando, aparecerá "WSJT DATA".

---

## 📝 Personalização

Clique no botão **⚙ CONFIG** na interface para ajustar:
* **Intervalo:** Tempo de permanência em cada banda.
* **Horários:** Definição de início do dia e fim do dia (para alternar as listas de bandas).
* **Bandas:** Selecione quais bandas quer varrer.

---

## 📄 Licença

Este projeto é distribuído sob a licença **MIT**. Veja o arquivo `LICENSE` para mais detalhes.