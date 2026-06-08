import streamlit as st
import PyPDF2
import docx
import os
import pathlib
import markdown
from summarizer import extract_key_points_from_report
from fpdf import FPDF

st.set_page_config(page_title="AI 供应链新闻整理平台", layout="wide")

# ---------- 自定义 CSS 美化（保留原始列表和链接样式） ----------
st.markdown("""
<style>
    .brief-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    .brief-card h1 {
        color: #1e3c72;
        border-left: 5px solid #ff6b35;
        padding-left: 20px;
        margin-top: 0;
        font-size: 2.2rem;
    }
    .brief-card h2 {
        color: #2c3e50;
        background: rgba(255,107,53,0.1);
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 30px;
        font-size: 1.5rem;
        margin-top: 1.5rem;
    }
    .brief-card h3 {
        color: #34495e;
        margin-top: 1rem;
        font-weight: 600;
    }
    /* 保持列表原始样式：无背景，标准圆点，默认缩进 */
    .brief-card ul, .brief-card ol {
        background: transparent;
        padding-left: 2rem;
        margin: 0.5rem 0;
        border-radius: 0;
    }
    .brief-card li {
        margin: 0.25rem 0;
        list-style-type: disc;
        line-height: 1.5;
    }
    /* 保持链接原始样式：蓝色下划线 */
    .brief-card a {
        color: #0066cc;
        text-decoration: underline;
        border-bottom: none;
    }
    .brief-card a:hover {
        color: #004499;
    }
    .brief-card hr {
        margin: 1.5rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(to right, #ff6b35, #f5f7fa);
    }
    .brief-date {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-align: right;
        margin-bottom: 1rem;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# ---------- 使用绝对路径定位简报目录 ----------
APP_DIR = pathlib.Path(__file__).parent
BRIEF_DIR = APP_DIR / "daily_briefs"

# ---------- 侧边栏语言选择 ----------
lang = st.sidebar.selectbox("Language / 语言", ["中文", "English"])
is_zh = (lang == "中文")

# ---------- 界面文本字典 ----------
if is_zh:
    title = "📦 AI 供应链新闻整理平台"
    tab1_name = "📰 每日自动简报"
    tab2_name = "📁 上传报告整理"
    tab1_header = "Supply Chain 24/7 每日新闻简报"
    tab1_caption = "系统每天 8:00 自动抓取并生成，最新简报如下："
    select_date_label = "选择日期"
    no_brief_yet = "暂无简报，请检查定时任务是否运行。"
    tab2_header = "上传供应链报告（PDF/Word/TXT）"
    tab2_desc = "上传文件后，AI 将自动提取关键信息并整理成结构化摘要。"
    upload_label = "选择文件"
    preview_label = "原始文本预览（前2000字符）"
    analyze_btn = "开始 AI 整理"
    analyzing_spinner = "DeepSeek 正在分析报告，请稍候..."
    done_msg = "整理完成！"
    download_md_label = "下载整理结果（Markdown）"
    download_pdf_label = "下载整理结果（PDF）"
    error_file_read = "文件读取错误："
    error_no_text = "未能提取到文本内容，请检查文件。"
    error_unsupported = "不支持的文件格式"
    warning_font = "未找到中文字体，PDF 可能无法正常显示中文。"
    brief_dir_warning = "简报目录未创建。"
else:
    title = "📦 AI Supply Chain News Platform"
    tab1_name = "📰 Daily Brief"
    tab2_name = "📁 Upload Report"
    tab1_header = "Supply Chain 24/7 Daily News Brief"
    tab1_caption = "Automatically fetched and summarized at 8:00 AM daily. Latest brief:"
    select_date_label = "Select Date"
    no_brief_yet = "No brief available yet. Please check if the scheduled task is running."
    tab2_header = "Upload Supply Chain Report (PDF/Word/TXT)"
    tab2_desc = "Upload a file and AI will extract key information and structure a summary."
    upload_label = "Choose a file"
    preview_label = "Raw text preview (first 2000 characters)"
    analyze_btn = "Start AI Analysis"
    analyzing_spinner = "DeepSeek is analyzing the report, please wait..."
    done_msg = "Analysis complete!"
    download_md_label = "Download Summary (Markdown)"
    download_pdf_label = "Download Summary (PDF)"
    error_file_read = "File read error: "
    error_no_text = "No text could be extracted. Please check the file."
    error_unsupported = "Unsupported file format"
    warning_font = "Chinese font not found, PDF may not display Chinese correctly."
    brief_dir_warning = "Brief directory not created."

# ---------- PDF 生成函数（修正参数） ----------
def markdown_to_pdf(md_text, font_warning_msg):
    """将 Markdown 文本转为 PDF 字节数据"""
    pdf = FPDF(format='A4')
    pdf.set_margins(left=15, top=15, right=15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # 尝试加载中文字体（仅当系统存在时）
    font_path = None
    possible_fonts = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc"
    ]
    for path in possible_fonts:
        if os.path.exists(path):
            font_path = path
            break
    if font_path:
        pdf.add_font("ChineseFont", "", font_path, uni=True)
        pdf.set_font("ChineseFont", "", 10)
    else:
        pdf.set_font("Helvetica", "", 10)
        st.warning(font_warning_msg)
    
    import re
    def break_long_words(text, max_len=80):
        return re.sub(
            r'\S{' + str(max_len) + ',}',
            lambda m: ' '.join([m.group(0)[i:i+max_len] for i in range(0, len(m.group(0)), max_len)]),
            text
        )
    processed_text = break_long_words(md_text, 80)
    pdf.write(h=5, txt=processed_text)
    return bytes(pdf.output(dest='S'))

# ---------- 主界面 ----------
st.title(title)

tab1, tab2 = st.tabs([tab1_name, tab2_name])

with tab1:
    st.header(tab1_header)
    st.caption(tab1_caption)
    
    if BRIEF_DIR.exists():
        files = [f.name for f in BRIEF_DIR.iterdir() if f.is_file()]
        files.sort(reverse=True)
        suffix = "_zh.md" if is_zh else "_en.md"
        lang_files = [f for f in files if f.endswith(suffix)]
        if lang_files:
            selected_file = st.selectbox(select_date_label, lang_files)
            if selected_file:
                file_path = BRIEF_DIR / selected_file
                with open(file_path, "r", encoding="utf-8") as f:
                    md_content = f.read()
                
                # 将 Markdown 转换为 HTML 并嵌入卡片
                html_content = markdown.markdown(md_content, extensions=['extra'])
                date_part = selected_file.split('_')[0]
                fancy_html = f"""
                <div class="brief-card">
                    <div class="brief-date">📅 {date_part}</div>
                    {html_content}
                </div>
                """
                st.markdown(fancy_html, unsafe_allow_html=True)
        else:
            st.info(no_brief_yet)
    else:
        st.info(brief_dir_warning)

with tab2:
    st.header(tab2_header)
    st.markdown(tab2_desc)
    uploaded_file = st.file_uploader(upload_label, type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        file_type = uploaded_file.name.split(".")[-1].lower()
        text = ""
        try:
            if file_type == "pdf":
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            elif file_type == "docx":
                doc = docx.Document(uploaded_file)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            elif file_type == "txt":
                text = uploaded_file.getvalue().decode("utf-8")
            else:
                st.error(error_unsupported)
                st.stop()
        except Exception as e:
            st.error(f"{error_file_read}{e}")
            st.stop()
        
        if not text.strip():
            st.warning(error_no_text)
        else:
            with st.expander(preview_label):
                st.text(text[:2000])
            
            if st.button(analyze_btn):
                with st.spinner(analyzing_spinner):
                    try:
                        result = extract_key_points_from_report(text, language="zh" if is_zh else "en")
                    except Exception as e:
                        st.error(f"AI 分析失败 / AI analysis failed: {e}")
                        st.stop()
                st.success(done_msg)
                st.markdown(result)
                
                # Markdown 下载
                result_bytes = result.encode("utf-8")
                md_filename = f"{uploaded_file.name}_summary.md"
                st.download_button(
                    label=download_md_label,
                    data=result_bytes,
                    file_name=md_filename,
                    mime="text/markdown"
                )
                
                # PDF 下载（传入 warning_font）
                try:
                    pdf_bytes = markdown_to_pdf(result, warning_font)
                    pdf_filename = f"{uploaded_file.name}_summary.pdf"
                    st.download_button(
                        label=download_pdf_label,
                        data=pdf_bytes,
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"PDF 生成失败 / PDF generation failed: {e}")
