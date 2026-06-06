import streamlit as st
import PyPDF2
import docx
import os
from summarizer import extract_key_points_from_report

if "DEEPSEEK_API_KEY" not in os.environ:
    # 如果本地运行时没有环境变量，尝试从 st.secrets 获取（只在云端有效）
    try:
        os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]
    except:
        pass

st.set_page_config(page_title="供应链新闻整理平台", layout="wide")
st.title("📦 AI 供应链新闻整理平台")

tab1, tab2 = st.tabs(["📰 每日自动简报", "📁 上传报告整理"])

with tab1:
    st.header("Supply Chain 24/7 每日新闻简报")
    st.caption("系统每天 8:00 自动抓取并生成，最新简报如下：")
    brief_dir = "daily_briefs"
    if os.path.exists(brief_dir):
        files = sorted(os.listdir(brief_dir), reverse=True)
        if files:
            selected_file = st.selectbox("选择日期", files)
            if selected_file:
                with open(os.path.join(brief_dir, selected_file), "r", encoding="utf-8") as f:
                    st.markdown(f.read())
        else:
            st.info("暂无简报，请检查定时任务是否运行。")
    else:
        st.info("简报目录未创建。")

with tab2:
    st.header("上传供应链报告（PDF/Word/TXT）")
    st.markdown("上传文件后，AI 将自动提取关键信息并整理成结构化摘要。")
    uploaded_file = st.file_uploader("选择文件", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        file_type = uploaded_file.name.split(".")[-1].lower()
        text = ""
        try:
            if file_type == "pdf":
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            elif file_type == "docx":
                doc = docx.Document(uploaded_file)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            elif file_type == "txt":
                text = uploaded_file.getvalue().decode("utf-8")
            else:
                st.error("不支持的文件格式")
        except Exception as e:
            st.error(f"文件读取错误：{e}")
            st.stop()
        
        if not text.strip():
            st.warning("未能提取到文本内容，请检查文件。")
        else:
            with st.expander("原始文本预览（前2000字符）"):
                st.text(text[:2000])
            
            if st.button("开始 AI 整理"):
                with st.spinner("DeepSeek 正在分析报告，请稍候..."):
                    result = extract_key_points_from_report(text)
                st.success("整理完成！")
                st.markdown(result)
                
                result_bytes = result.encode("utf-8")
                st.download_button(
                    label="下载整理结果（Markdown）",
                    data=result_bytes,
                    file_name=f"{uploaded_file.name}_summary.md",
                    mime="text/markdown"
                )
