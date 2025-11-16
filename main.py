import json
import markdown
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="微信公众号HTML生成器")


class ArticleItem(BaseModel):
    title: str
    summary: str
    url: str


class ConvertRequest(BaseModel):
    articles: List[ArticleItem] = Field(..., description="文章列表")


class ConvertResponse(BaseModel):
    html: str = Field(..., description="生成的HTML内容")


def convert_markdown_to_html(markdown_text: str) -> str:
    """将markdown文本转换为HTML"""
    md = markdown.Markdown(extensions=['extra', 'nl2br'])
    html = md.convert(markdown_text)
    return html


def generate_html_content(articles: List[Dict[str, Any]]) -> str:
    """生成微信公众号HTML内容片段"""
    html_parts = []
    
    for article in articles:
        title = article.get('title', '')
        summary = article.get('summary', '')
        url = article.get('url', '')
        
        # 转换markdown摘要为HTML
        summary_html = convert_markdown_to_html(summary)
        
        # 生成单个条目的HTML
        article_html = f"""
<div style="margin-bottom: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff;">
    <h2 style="margin: 0 0 15px 0; font-size: 20px; font-weight: bold; color: #333; line-height: 1.5;">
        {title}
    </h2>
    <div style="margin-bottom: 15px; font-size: 16px; line-height: 1.8; color: #555;">
        {summary_html}
    </div>
    <a href="{url}" target="_blank" style="display: inline-block; padding: 8px 16px; background-color: #007bff; color: #fff; text-decoration: none; border-radius: 4px; font-size: 14px; margin-top: 10px;">
        查看原文 →
    </a>
</div>
"""
        html_parts.append(article_html)
    
    # 合并所有条目
    html_content = ''.join(html_parts)
    
    # 添加整体样式包装
    final_html = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #fff;">
{html_content}
</div>
"""
    
    return final_html


def apply_inline_styles(html: str) -> str:
    """为HTML元素添加内联样式，确保微信公众号兼容性"""
    import re
    
    # 处理段落（只替换没有style属性的p标签）
    html = re.sub(r'<p(?![^>]*style=)', '<p style="margin: 10px 0; line-height: 1.8;"', html)
    
    # 处理列表（只替换没有style属性的标签）
    html = re.sub(r'<ul(?![^>]*style=)', '<ul style="margin: 10px 0; padding-left: 25px; line-height: 1.8;"', html)
    html = re.sub(r'<ol(?![^>]*style=)', '<ol style="margin: 10px 0; padding-left: 25px; line-height: 1.8;"', html)
    html = re.sub(r'<li(?![^>]*style=)', '<li style="margin: 5px 0;"', html)
    
    # 处理粗体（只替换没有style属性的strong标签）
    html = re.sub(r'<strong(?![^>]*style=)', '<strong style="font-weight: bold; color: #333;"', html)
    
    # 处理引用块（只替换没有style属性的blockquote标签）
    html = re.sub(r'<blockquote(?![^>]*style=)', '<blockquote style="margin: 15px 0; padding: 10px 15px; background-color: #f0f0f0; border-left: 4px solid #ccc; color: #666; font-style: italic;"', html)
    
    # 处理标题（只替换没有style属性的标题标签，因为summary中的markdown可能包含标题）
    html = re.sub(r'<h1(?![^>]*style=)', '<h1 style="font-size: 24px; font-weight: bold; margin: 20px 0 15px 0; color: #333; line-height: 1.4;"', html)
    html = re.sub(r'<h3(?![^>]*style=)', '<h3 style="font-size: 18px; font-weight: bold; margin: 15px 0 10px 0; color: #333; line-height: 1.4;"', html)
    html = re.sub(r'<h4(?![^>]*style=)', '<h4 style="font-size: 16px; font-weight: bold; margin: 12px 0 8px 0; color: #333; line-height: 1.4;"', html)
    # 注意：h2标签在generate_html_content中已经有样式，这里不处理
    
    return html


@app.post("/convert", response_model=ConvertResponse)
async def convert_to_html(request: ConvertRequest):
    """API端点：接收JSON数据，返回生成的HTML字符串"""
    try:
        articles_data = [article.dict() for article in request.articles]
        html_content = generate_html_content(articles_data)
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
            articles = json.load(f)
        
        # 生成HTML
        html_content = generate_html_content(articles)
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
