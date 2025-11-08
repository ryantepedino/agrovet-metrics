# app/dashboards/app_streamlit.py
import streamlit as st
import requests
from datetime import date
import urllib.parse

st.set_page_config(page_title="Métricas AgroVet", page_icon="🐄", layout="wide")

# ==========================================
# 🔹 Configurações
# ==========================================
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.sidebar.title("Métricas AgroVet")
opcao = st.sidebar.radio("Navegação", ["Secretário(a) 📋", "Resultados 📊", "Ajuda ❄️"])

# ==========================================
# 🔹 Verifica status da API
# ==========================================
def check_api():
    try:
        r = requests.get(f"{API_URL}/")
        if r.status_code == 200:
            return True
    except Exception:
        pass
    return False

api_ok = check_api()

# ==========================================
# 🔹 Página — Secretário(a)
# ==========================================
if opcao == "Secretário(a) 📋":
    st.header("📋 Registrar Medições")
    st.subheader("Métricas por fazenda")

    if not api_ok:
        st.warning("⚠️ API offline. Inicie o backend antes de registrar dados.")
    else:
        # Busca lista de fazendas
        try:
            response = requests.get(f"{API_URL}/fazendas/")
            if response.status_code == 200:
                fazendas = response.json()
                if fazendas:
                    nomes = [f["nome"] for f in fazendas]
                    selecionada = st.selectbox("Selecione a Fazenda", nomes)
                    id_fazenda = next(f["id"] for f in fazendas if f["nome"] == selecionada)
                else:
                    st.warning("Nenhuma fazenda cadastrada.")
                    id_fazenda = None
            else:
                st.warning("⚠️ Falha ao carregar fazendas.")
                id_fazenda = None
        except Exception as e:
            st.warning(f"⚠️ Erro ao buscar fazendas: {e}")
            id_fazenda = None

        if id_fazenda:
            st.info(f"🏷️ Fazenda selecionada: **{selecionada} (ID {id_fazenda})**")

            st.date_input("Data da medição", value=date.today())
            st.number_input("Aptas", min_value=0)
            st.number_input("Inseminadas", min_value=0)
            st.number_input("Gestantes", min_value=0)
            st.number_input("Partos realizados", min_value=0)
            st.success("✅ Dados prontos para envio (integração futura).")

# ==========================================
# 🔹 Página — Resultados
# ==========================================
elif opcao == "Resultados 📊":
    st.header("📊 Resultados e Relatórios")

    if not api_ok:
        st.warning("⚠️ API offline. Inicie o backend antes de gerar relatórios.")
    else:
        try:
            response = requests.get(f"{API_URL}/fazendas/")
            if response.status_code == 200:
                fazendas = response.json()
                if fazendas:
                    nomes = [f["nome"] for f in fazendas]
                    selecionada = st.selectbox("Selecione a Fazenda", nomes)
                    id_fazenda = next(f["id"] for f in fazendas if f["nome"] == selecionada)
                else:
                    st.warning("Nenhuma fazenda cadastrada.")
                    id_fazenda = None
            else:
                st.warning("⚠️ Erro ao carregar fazendas.")
                id_fazenda = None
        except Exception as e:
            st.warning(f"⚠️ Erro ao conectar à API: {e}")
            id_fazenda = None

        if id_fazenda:
            st.info(f"📄 Fazenda selecionada: **{selecionada} (ID {id_fazenda})**")

            inicio = st.date_input("Data inicial", value=date(2025, 9, 1))
            fim = st.date_input("Data final", value=date.today())

            col1, col2, col3 = st.columns(3)

            # ------------------------------------------
            # XLSX
            # ------------------------------------------
            with col1:
                if st.button("📊 Gerar XLSX"):
                    try:
                        r = requests.get(f"{API_URL}/relatorio/fazenda/{id_fazenda}.xlsx",
                                         params={"inicio": inicio, "fim": fim})
                        if r.status_code == 200:
                            st.download_button("⬇️ Baixar XLSX",
                                               r.content,
                                               file_name=f"Relatorio_{selecionada}.xlsx")
                            # Gera link de envio
                            mensagem = (
                                f"📈 Relatório AgroVet Metrics — {selecionada}\n"
                                f"Período: {inicio} a {fim}\n"
                                "Segue em anexo o relatório de métricas reprodutivas."
                            )
                            url_msg = urllib.parse.quote(mensagem)
                            link_whatsapp = f"https://wa.me/?text={url_msg}"
                            st.markdown(f"[📤 Enviar via WhatsApp]({link_whatsapp})", unsafe_allow_html=True)
                        else:
                            st.error("Erro ao gerar XLSX.")
                    except Exception as e:
                        st.error(f"Falha: {e}")

            # ------------------------------------------
            # PDF
            # ------------------------------------------
            with col2:
                if st.button("🧾 Gerar PDF"):
                    try:
                        r = requests.get(f"{API_URL}/relatorio/fazenda/{id_fazenda}.pdf",
                                         params={"inicio": inicio, "fim": fim})
                        if r.status_code == 200:
                            st.download_button("⬇️ Baixar PDF",
                                               r.content,
                                               file_name=f"Relatorio_{selecionada}.pdf")
                            # Gera link de envio
                            mensagem = (
                                f"🧾 Relatório AgroVet Metrics — {selecionada}\n"
                                f"Período: {inicio} a {fim}\n"
                                "Segue em anexo o relatório reprodutivo em PDF."
                            )
                            url_msg = urllib.parse.quote(mensagem)
                            link_whatsapp = f"https://wa.me/?text={url_msg}"
                            st.markdown(f"[📤 Enviar via WhatsApp]({link_whatsapp})", unsafe_allow_html=True)
                        else:
                            st.error("Erro ao gerar PDF.")
                    except Exception as e:
                        st.error(f"Falha: {e}")

            with col3:
                st.info("💬 Após gerar o relatório, clique em **Enviar via WhatsApp** para compartilhar com o cliente.")

# ==========================================
# 🔹 Página — Ajuda
# ==========================================
elif opcao == "Ajuda ❄️":
    st.header("🧠 Ajuda e status")

    st.markdown("""
    **Como usar (em campo):**
    1. Vá em **Secretário(a)** → selecione a fazenda → informe `Aptas`, `Inseminadas`, `Gestantes`, `Partos`.
    2. Vá em **Resultados** → escolha o período → clique em **Gerar PDF** ou **Gerar XLSX**.
    3. Clique em **Enviar via WhatsApp** para compartilhar o relatório com o produtor.

    **Observações:**
    - *Partos realizados*: soma de eventos de parto no período.
    - *Partos previstos*: gestantes cujo parto estimado (dados + 283 dias) caiam no período.
    """)

    st.subheader("Status da API")
    if api_ok:
        st.success(f"✅ API online: {API_URL}")
    else:
        st.error("❌ API offline ou inacessível.")
