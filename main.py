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


class ConvertRequest(BaseModel):
    articles: List[ArticleItem] = Field(..., description="文章列表")


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


def generate_html_content(articles: List[Dict[str, Any]]) -> str:
    """生成微信公众号HTML内容片段"""
    html_parts = []
    
    for article in articles:
        title = article.get('title', '')
        summary = article.get('summary', '')
        url = article.get('url', '')
        
        # 转换markdown摘要为HTML
        summary_html = convert_markdown_to_html(summary)
        
        # 根据链接类型决定显示方式
        if is_wechat_url(url):
            # 微信公众号链接，显示为可点击链接（柔和简洁的按钮样式）
            url_display = f'<div style="margin-top: 18px;"><a href="{url}" target="_blank" style="display: inline-block; color: #7B8FA1; text-decoration: none; font-size: 14px; padding: 8px 18px; border-radius: 8px; font-weight: 400; box-shadow: 0 1px 3px rgba(107, 182, 255, 0.2);">查看原文 →</a></div>'
        else:
            # 非微信公众号链接，只显示原始链接文本
            url_display = f'<div style="margin-top: 18px;"><span style="display: inline-block; color: #7B8FA1; font-size: 14px; background-color: #F0F4F8; padding: 8px 16px; border-radius: 8px;">[原文链接]: {url}</span></div>'
        
        # 生成单个条目的HTML（简约扁平化卡片设计）
        # 使用循环颜色：蓝色、青色、橙色、紫色
        colors = [
            {'dot': '#4A90E2', 'title': '#2C5F8D', 'bg': '#E8F4FD'},
            {'dot': '#00C9A7', 'title': '#008B6B', 'bg': '#E0F7F4'},
            {'dot': '#FF8C42', 'title': '#CC6D35', 'bg': '#FFF4ED'},
            {'dot': '#9B59B6', 'title': '#7D3C98', 'bg': '#F4E8F7'}
        ]
        color_scheme = colors[len(html_parts) % len(colors)]
        
        article_html = f"""
<div style="margin: 25px auto; max-width: 600px; background-color: {color_scheme['bg']}; border-radius: 16px; padding: 25px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);">
    <table width="100%" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; border: none;">
        <tr>
            <!-- 左侧彩色圆点装饰 -->
            <td width="30" valign="top" style="width: 30px; vertical-align: top; padding-top: 4px; border: none;">
                <div style="width: 12px; height: 12px; background-color: {color_scheme['dot']}; border-radius: 50%; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);"></div>
            </td>
            <!-- 右侧内容区域 -->
            <td valign="top" style="vertical-align: top; padding-left: 18px; border: none;">
                <h3 style="color: {color_scheme['title']}; font-size: 22px; font-weight: 600; margin-top: 0; margin-bottom: 16px; line-height: 1.4;">
                    {title}
                </h3>
                <div style="color: #4A5568; font-size: 15px; line-height: 1.75; margin-top: 0; margin-bottom: 0;">
                    {summary_html}
                </div>
                {url_display}
            </td>
        </tr>
    </table>
</div>
"""
        html_parts.append(article_html)
    
    # 合并所有条目
    html_content = ''.join(html_parts)
    
    # 获取当前日期
    current_date = datetime.now().strftime('%m月%d日')
    
    # 添加装饰头部（简约扁平化风格）
    header_decorator = f"""
<div style="text-align: center; margin-bottom: 40px; padding: 30px 20px;">
    <div style="display: inline-block; background: linear-gradient(135deg, #E8F4FD 0%, #E0F7F4 50%, #FFF4ED 100%); padding: 20px 40px; border-radius: 24px; box-shadow: 0 4px 16px rgba(74, 144, 226, 0.1);">
        <h1 style="color: #2C5F8D; font-size: 28px; font-weight: 600; margin: 0; letter-spacing: 1px;">{current_date} · 新闻资讯</h1>
        <div style="color: #7B8FA1; font-size: 14px; margin-top: 8px; font-weight: 400;">Daily AI News</div>
    </div>
</div>
"""
    
    # 添加装饰尾部（简约扁平化风格）
    footer_decorator = """
<div style="margin-top: 50px; text-align: center; padding: 20px;">
    <table width="100%" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; border: none;">
        <tr>
            <td align="center" style="text-align: center; border: none;">
                <table cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; margin: 0 auto; border: none;">
                    <tr>
                        <td style="width: 40px; height: 2px; background: linear-gradient(90deg, transparent, #4A90E2, transparent); border: none;"></td>
                        <td style="padding: 0 12px; color: #7B8FA1; font-size: 14px; font-weight: 400; white-space: nowrap; border: none;">END</td>
                        <td style="width: 40px; height: 2px; background: linear-gradient(90deg, transparent, #4A90E2, transparent); border: none;"></td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</div>
"""
    
    # 添加整体样式包装（清爽的浅色背景）
    final_html = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif; padding: 30px 20px; background: linear-gradient(180deg, #FAFBFC 0%, #F5F7FA 100%); min-height: 100vh;">
{header_decorator}
{html_content}
{footer_decorator}
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
