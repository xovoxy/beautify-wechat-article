import json
import markdown
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="微信公众号HTML生成器")


class ArticleItem(BaseModel):
    title: str
    summary: str
    url: str
    newstype: str  # 新闻类型 ai_news model ai_product


class ConvertRequest(BaseModel):
    articles: List[ArticleItem] = Field(..., description="文章列表")
    summary: str = Field(..., description="摘要")


class ConvertResponse(BaseModel):
    html: str = Field(..., description="生成的HTML内容")


def convert_markdown_to_html(markdown_text: str) -> str:
    """将markdown文本转换为HTML"""
    md = markdown.Markdown(extensions=['extra', 'nl2br'])
    html = md.convert(markdown_text)
    return html


def is_wechat_url(url: str) -> bool:
    """判断是否是微信公众号链接"""
    if not url:
        return False
    return 'mp.weixin.qq.com' in url.lower()


def generate_html_content(articles: List[Dict[str, Any]], summary: str = '') -> str:
    """生成微信公众号HTML内容片段，使用ainews模板样式"""
    # 类型标题映射
    type_title_map = {
        "ai_news": "新闻资讯",
        "model": "模型资讯",
        "ai_product": "AI产品资讯"
    }
    
    # 按类型分组文章
    articles_by_type = {}
    for article in articles:
        news_type = article.get('newstype', 'ai_news')
        if news_type not in articles_by_type:
            articles_by_type[news_type] = []
        articles_by_type[news_type].append(article)
    
    # 获取当前日期
    current_date = datetime.now().strftime('%m月%d日')
    
    # 生成头部（使用动态日期，保持模板样式）
    header_section = f"""
<section style="text-align:center;margin-bottom:unset;">
    <section
        style="border-width:3px;border-bottom-style:solid;border-color:rgb(0, 0, 34);padding:5px 25px;display:inline-block;box-sizing:border-box;margin-bottom:unset;">
        <p style="letter-spacing:4px;"><strong><span style="font-size:20px;"><span leaf="">{current_date} · 每日资讯</span></span></strong></p>
    </section>
    <p style="letter-spacing:0px;"><span style="font-size:20px;"><span leaf="">Daily AI News</span></span></p>
    <section
        style="margin-left:auto;margin-right:auto;width:60px;height:10px;background-color:rgb(67, 212, 201);margin-bottom:unset;overflow:hidden;line-height:0;">
        <span leaf=""><br class="ProseMirror-trailingBreak"></span></section>
</section>
<p><span leaf=""><br class="ProseMirror-trailingBreak"></span></p>
"""
    
    # 生成新闻概览部分（如果提供了summary）
    overview_section = ''
    if summary:
        # summary 是纯文本，不需要 markdown 转换
        overview_section = f"""
<section style="margin-bottom:unset;">
    <section style="vertical-align:top;margin-bottom:unset;">
        <section style="margin-left:50px;margin-bottom:-20px;">
            <p style="letter-spacing:3px;"><span leaf="">新闻概览</span></p>
        </section>
        <section
            style="width:15px;height:15px;margin-right:auto;margin-left:10px;margin-bottom:3px;background-color:rgb(67, 212, 201);overflow:hidden;line-height:0;">
            <span leaf=""><br class="ProseMirror-trailingBreak"></span></section>
        <section style="width:233px;margin-right:auto;margin-bottom:unset;">
            <section
                style="width:235px;height:2px;margin-left:3px;margin-bottom:-16px;background-color:rgb(67, 212, 201);overflow:hidden;line-height:0;">
                <span leaf=""><br class="ProseMirror-trailingBreak"></span></section>
            <section
                style="width:2px;height:85px;margin-left:34px;background-color:rgb(67, 212, 201);margin-bottom:unset;overflow:hidden;line-height:0;">
                <span leaf=""><br class="ProseMirror-trailingBreak"></span></section>
        </section>
        <section
            style="padding-left:50px;padding-right:20px;margin-top:-55px;font-size:18px;color:rgb(67, 212, 201);box-sizing:border-box;margin-bottom:unset;">
            <div style="font-size:18px;color:rgb(67, 212, 201);">{summary}</div>
        </section>
    </section>
</section>
<p><span leaf=""><br class="ProseMirror-trailingBreak"></span></p>
"""
    
    # 按类型顺序生成分组内容
    type_order = ["ai_news", "model", "ai_product"]
    grouped_sections = []
    
    for news_type in type_order:
        if news_type not in articles_by_type or len(articles_by_type[news_type]) == 0:
            continue
        
        type_title = type_title_map.get(news_type, news_type)
        type_articles = articles_by_type[news_type]
        type_index = 1  # 该类型的文章编号，从1开始
        
        # 生成类型分组标题
        type_header_section = f"""
<section style="text-align:center;margin-bottom:unset;">
    <section
        style="border-width:3px;border-bottom-style:solid;border-color:rgb(0, 0, 34);padding:5px 25px;display:inline-block;box-sizing:border-box;margin-bottom:unset;">
        <p style="letter-spacing:4px;"><strong><span style="font-size:20px;"><span leaf="">{type_title}</span></span></strong></p>
    </section>
    <section
        style="margin-left:auto;margin-right:auto;width:60px;height:10px;background-color:rgb(67, 212, 201);margin-bottom:unset;overflow:hidden;line-height:0;">
        <span leaf=""><br class="ProseMirror-trailingBreak"></span></section>
</section>
<p><span leaf=""><br class="ProseMirror-trailingBreak"></span></p>
"""
        grouped_sections.append(type_header_section)
        
        # 生成该类型下的文章列表
        for article in type_articles:
            title = article.get('title', '')
            article_summary = article.get('summary', '')
            url = article.get('url', '')
            
            # 转换markdown摘要为HTML
            summary_html = convert_markdown_to_html(article_summary)
            
            # 生成URL显示部分
            if url:
                if is_wechat_url(url):
                    url_display = f'<p style="margin-top: 12px;"><a href="{url}" target="_blank" style="color: rgb(67, 212, 201); text-decoration: none; font-size: 14px;">查看原文 →</a></p>'
                else:
                    url_display = f'<p style="margin-top: 12px;"><span style="color: rgb(136, 136, 136); font-size: 14px;">[原文链接]: {url}</span></p>'
            else:
                url_display = ''
            
            # 生成编号条目（使用模板的旋转方块装饰样式）
            article_section = f"""
<section style="margin-bottom:unset;">
    <section style="margin:10px;">
        <section
            style="display:inline-block;background-color:rgb(113, 232, 222);width:35px;height:35px;margin-bottom:unset;overflow:hidden;line-height:0;transform:rotate(45deg);-webkit-transform:rotate(45deg);-moz-transform:rotate(45deg);-ms-transform:rotate(45deg);-o-transform:rotate(45deg);">
            <span leaf=""><br class="ProseMirror-trailingBreak"></span></section>
        <section
            style="background-color:rgb(113, 232, 222);margin-left:-10px;display:inline-block;width:30px;height:30px;margin-bottom:unset;overflow:hidden;line-height:0;transform:rotate(45deg);-webkit-transform:rotate(45deg);-moz-transform:rotate(45deg);-ms-transform:rotate(45deg);-o-transform:rotate(45deg);">
            <span leaf=""><br class="ProseMirror-trailingBreak"></span></section>
    </section>
    <section
        style="margin-left:20px;margin-top:-50px;margin-bottom:unset;transform:rotate(0deg);-webkit-transform:rotate(0deg);-moz-transform:rotate(0deg);-ms-transform:rotate(0deg);-o-transform:rotate(0deg);">
        <p><strong><span style="font-size:18px;"><span leaf="">no.{type_index} &nbsp; {title}</span></span></strong></p>
    </section>
</section>
<p><span leaf=""><br class="ProseMirror-trailingBreak"></span></p>
<section style="margin-bottom:unset;">
    <div style="font-size:15px;letter-spacing:2px;color:#333333;font-family:微软雅黑, Arial;">{summary_html}</div>
{url_display}
</section>
<p><span leaf=""><br class="ProseMirror-trailingBreak"></span></p>
"""
            grouped_sections.append(article_section)
            type_index += 1
    
    # 生成尾部（使用模板的end样式）
    footer_section = """
<section style="margin-bottom:unset;">
    <section style="text-align:center;margin-bottom:unset;">
        <section
            style="display:inline-block;background-color:rgb(113, 232, 222);width:35px;height:35px;margin-bottom:unset;overflow:hidden;line-height:0;transform:rotate(45deg);-webkit-transform:rotate(45deg);-moz-transform:rotate(45deg);-ms-transform:rotate(45deg);-o-transform:rotate(45deg);">
            <span leaf=""><br class="ProseMirror-trailingBreak"></span></section>
        <section
            style="background-color:rgb(113, 232, 222);margin-left:-10px;display:inline-block;width:30px;height:30px;margin-bottom:unset;overflow:hidden;line-height:0;transform:rotate(45deg);-webkit-transform:rotate(45deg);-moz-transform:rotate(45deg);-ms-transform:rotate(45deg);-o-transform:rotate(45deg);">
            <span leaf=""><br class="ProseMirror-trailingBreak"></span></section>
    </section>
    <section
        style="margin-top:-40px;margin-bottom:unset;transform:rotate(0deg);-webkit-transform:rotate(0deg);-moz-transform:rotate(0deg);-ms-transform:rotate(0deg);-o-transform:rotate(0deg);">
        <p style="text-align:center;"><span
                style="font-size:18px;color:#ffffff;"><strong><span
                        leaf="">end</span></strong></span></p>
    </section>
</section>
<p><span leaf=""><br class="ProseMirror-trailingBreak"></span></p>
"""
    
    # 组合所有部分，使用模板的包装结构
    content_html = header_section + overview_section + ''.join(grouped_sections) + footer_section
    
    # 使用模板的完整包装结构
    final_html = f"""
<div>
    <div></div>
    <div id="ueditor_0" class="mock-iframe">
        <div class="mock-iframe-document">
            <div class="mock-iframe-body">
                <div spellcheck="false" lang="en" class="view rich_media_content autoTypeSetting24psection">
                    <div contenteditable="true" translate="no" class="ProseMirror"
                        style="padding: 0px 4px; min-height: 949px;">
                        <section style="margin-bottom:unset;" data-pm-slice="0 0 []">
{content_html}
                        </section>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div></div>
</div>
"""
    
    return final_html


def apply_inline_styles(html: str) -> str:
    """为HTML元素添加内联样式，确保微信公众号兼容性（简约扁平化风格）"""
    import re
    
    # 处理段落（只替换没有style属性的p标签）
    html = re.sub(r'<p(?![^>]*style=)', '<p style="margin: 0 0 12px 0; line-height: 1.75; color: #4A5568;"', html)
    
    # 处理列表（只替换没有style属性的标签）
    html = re.sub(r'<ul(?![^>]*style=)', '<ul style="margin: 12px 0; padding-left: 24px; line-height: 1.75; color: #4A5568;"', html)
    html = re.sub(r'<ol(?![^>]*style=)', '<ol style="margin: 12px 0; padding-left: 24px; line-height: 1.75; color: #4A5568;"', html)
    html = re.sub(r'<li(?![^>]*style=)', '<li style="margin: 6px 0; color: #4A5568;"', html)
    
    # 处理粗体（只替换没有style属性的strong标签）
    html = re.sub(r'<strong(?![^>]*style=)', '<strong style="font-weight: 600; color: #2C5F8D;"', html)
    
    # 处理引用块（只替换没有style属性的blockquote标签，扁平化风格）
    html = re.sub(r'<blockquote(?![^>]*style=)', '<blockquote style="margin: 16px 0; padding: 16px 20px; background: linear-gradient(135deg, #E8F4FD 0%, #E0F7F4 100%); border-left: 4px solid #4A90E2; border-radius: 8px; color: #4A5568; font-style: normal;"', html)
    
    # 处理标题（只替换没有style属性的标题标签，因为summary中的markdown可能包含标题）
    html = re.sub(r'<h1(?![^>]*style=)', '<h1 style="font-size: 26px; font-weight: 600; margin: 24px 0 16px 0; color: #2C5F8D; line-height: 1.4;"', html)
    html = re.sub(r'<h3(?![^>]*style=)', '<h3 style="font-size: 20px; font-weight: 600; margin: 20px 0 12px 0; color: #2C5F8D; line-height: 1.4;"', html)
    html = re.sub(r'<h4(?![^>]*style=)', '<h4 style="font-size: 18px; font-weight: 600; margin: 16px 0 10px 0; color: #2C5F8D; line-height: 1.4;"', html)
    # 注意：h2标签在generate_html_content中已经有样式，这里不处理
    
    return html


@app.post("/convert", response_model=ConvertResponse)
async def convert_to_html(request: ConvertRequest):
    """API端点：接收JSON数据，返回生成的HTML字符串"""
    try:
        articles_data = [article.dict() for article in request.articles]
        html_content = generate_html_content(articles_data, summary=request.summary)
        # 应用内联样式
        html_content = apply_inline_styles(html_content)
        return ConvertResponse(html=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成HTML时出错: {str(e)}")


def main():
    """命令行功能：从date.txt读取数据并生成HTML"""
    try:
        # 读取date.txt文件
        with open('date.txt', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 支持两种格式：直接是文章列表，或包含articles和summary的对象
        if isinstance(data, list):
            articles = data
            summary = ''
        else:
            articles = data.get('articles', [])
            summary = data.get('summary', '')
        
        # 生成HTML
        html_content = generate_html_content(articles, summary=summary)
        html_content = apply_inline_styles(html_content)
        
        # 直接输出到控制台
        print(html_content)
        
    except FileNotFoundError:
        print("错误: 找不到 date.txt 文件")
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 - {str(e)}")
    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    import sys
    
    # 如果作为API服务器运行
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # 命令行模式
        main()
