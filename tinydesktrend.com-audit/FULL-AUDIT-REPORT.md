# tinydesktrend.com SEO + GEO 审计

日期：2026-10-29。范围：sitemap 中 12 个页面加 /login/ 和 404 页。方法：本机 Chrome 抓取线上页面（Playwright），curl 检查响应头与跳转，再读 robots.txt、llms.txt 和结构化数据。未接入 Search Console、CrUX 和 AI 平台采样数据，所以本报告不判断排名、收录量或 AI 引用份额。框架：claude-seo（seo-audit）评分 + yao-geo-page-audit 五段链路（发现 → 候选 → 正文抽取 → 证据质量 → 生成引用）。

## 总分：74 / 100（业务类型：单一热点的付费 AI 视频生成工具）

| 类别 | 权重 | 得分 |
|---|---|---|
| 技术 SEO | 22% | 80 |
| 内容质量 | 23% | 60 |
| 页面 SEO | 20% | 80 |
| 结构化数据 | 10% | 65 |
| 性能 | 10% | 85 |
| AI 搜索就绪 | 10% | 75 |
| 图片 | 5% | 90 |

分数是我按 claude-seo 权重做的人工估算，不是工具测出的数值。

## 已经做对的

- 所有页面 200，404 页返回真实 404 且 noindex；/login/ 设了 noindex。
- www 和无斜杠地址都 301 到规范地址，/index.html 301 到 /。
- 每页都有唯一 title、description 和 canonical，只有一个 H1，lang=en。
- 正文在初始 HTML 里（静态生成），不依赖 JS 渲染。
- robots.txt 放行全部爬虫并显式允许 GPTBot、OAI-SearchBot、ClaudeBot、PerplexityBot、Google-Extended；用这些 UA 访问首页都返回 200。
- llms.txt 存在，列出了全部教程、FAQ 和政策页。
- 教程页先给结论（如 song 页的 “Short answer”），带日期和外部来源链接。
- 首页 LCP 约 340 ms，TTFB 约 110 ms（本机实验室数据，不是用户实测数据）。

## 问题清单

### High

1. **HTTP 不跳转 HTTPS。** `http://tinydesktrend.com/` 直接返回 200 页面，也没有 HSTS 头。同一内容存在两个协议版本，canonical 能缓解但不能代替跳转。修复：在 worker.js 里对 `http:` 请求 301 到 https，并加 `Strict-Transport-Security`；或在 Cloudflare 开启 Always Use HTTPS。
2. **教程内容偏薄，缺少作者和一手经验（E-E-A-T）。** 7 篇教程正文只有 158–354 词；没有作者、没有“关于我们”页；制作教程主要转述竞品（trendrecast 的 Hugging Face 博客）的技术文章。可我们自己就在跑这条生产流程（13 秒切点、MiniMax H3、浏览器内裁剪和加音轨），这部分一手信息没写出来。修复：每篇补到 600–900 词，加入自己的实测（成功率、失败案例、耗时、样片对比）；加作者署名和一个 About 页。
3. **品牌实体名称不统一。** 页面 logo 和 H1 叫 “Tiny Desk AI”，og:site_name、WebSite schema 和 llms.txt 叫 “Tiny Desk Trend”，域名是 tinydesktrend。AI 归纳品牌时容易把它当成两个实体。修复：定一个主名（建议 “Tiny Desk Trend”，与域名一致），另一个作为别名写进 schema 的 `alternateName`。

### Medium

4. **首页一打开就下载 2.8 MB 样片。** 页面加载后自动播放，sample.mp4 占首页传输量 2.8 MB 中的绝大部分，手机流量下影响明显。修复：重新压缩成约 1 MB 的 H.264 或 WebM；样片进入视口再播放（IntersectionObserver）。
5. **结构化数据不完整。**
   - Article 缺 `author`、`image`；`publisher` 没有 `logo` 和 `url`。
   - 没有 `Organization` 和 `BreadcrumbList`。
   - /guides/ 没有 `CollectionPage` 或 `ItemList`。
   - 首页的 WebApplication 可以补 `screenshot` 和 `video`（VideoObject，指向样片）。
6. **内链不足。** /faq/ 正文没有任何内链，song 页也没有；多数教程正文只有 1 个内链。修复：每篇教程末尾加“生成你的视频”按钮和 2–3 篇相关教程；FAQ 答案里链到对应教程。
7. **/guides/ 索引页太薄。** 只有 73 词；description 写“origin, how to make one, and the song”，实际有 7 篇。修复：每篇加一句摘要，改写 description，加 ItemList schema。
8. **所有页面共用旧版 og.png。** 分享图还是改版前的棕色 “TD” 设计，和新页面不一致，每篇教程也没有自己的分享图。修复：按新设计重做 og.png，教程页最好各有一张。
9. **引用来源依赖竞品。** 起源和制作教程把竞品博客当作主要出处。修复：补一手来源，如 TikTok 原帖链接和 NPR 页面，竞品博客只作补充。

### Low

10. 首页 meta description 171 字符，搜索结果会截断，压到 155 以内。
11. Privacy（40 字符）和 Terms（35 字符）的 description 太短，guides 的 title 只有 19 字符。
12. sitemap 的 lastmod 全部是同一天，以后应按每页真实修改日期写。
13. 首页和 /faq/ 都输出 FAQPage schema，内容重复。Google 从 2023 年起基本只给政府和医疗站展示 FAQ 富结果，这里主要对 AI 抽取有用；建议只在 /faq/ 保留完整版。HowTo 富结果已下线，schema 留着不影响。
14. Cloudflare Web Analytics 的 beacon 被站点 CSP 拦截（控制台报错），统计实际不生效。决定要统计就把 `static.cloudflareinsights.com` 加进 script-src，不要就在 Cloudflare 后台关掉自动注入。

## GEO 五段链路（yao-geo-page-audit）

| 阶段 | 状态 | 依据 |
|---|---|---|
| 发现 | 好 | robots 放行主要 AI 爬虫，sitemap 和 llms.txt 齐全（观察） |
| 检索候选 | 一般 | 关键词覆盖了 origin、song、template、generator、ideas，但缺 “tiny desk ai free” 和竞品对比类问题（推断） |
| 正文抽取 | 好 | 静态 HTML，结论先行，有表格（镜头时间表、歌曲事实表）和步骤（观察） |
| 证据质量 | 弱 | 无作者、无一手数据、主要出处是竞品博客（观察） |
| 生成引用 | 一般 | 品牌名不统一；缺少适合原样引用的自有事实，如“生成约 2 分钟，失败退积分”这类可核验的服务事实散落在页面里，没有集中成事实卡（推断） |

没有 AI 平台采样数据，以上不代表 ChatGPT、Perplexity 等平台的实际引用情况。

## 建议的执行顺序

1. 本周：HTTP→HTTPS 跳转加 HSTS（第 1 项）；统一品牌名（第 3 项）；压缩样片（第 4 项）；修正 description 长度（第 10、11 项）。
2. 下周：补全 schema（第 5 项）、内链（第 6 项）、guides 索引（第 7 项）、新 og 图（第 8 项）。
3. 本月：每篇教程补一手内容和作者，加 About 页，替换竞品出处（第 2、9 项）。

## 2026-10-29 修复记录

已修复并上线（Worker 版本 dab4c523）：第 1–8 项全部，第 9 项部分完成，以及第 10、11、12、13 项。

- 第 1 项：HTTP 301 跳转到 HTTPS；加了 HSTS（max-age 一年）。
- 第 2 项：教程扩写到 320–882 词，写入我们自己生成流程的事实（模型、13 秒参考片段、浏览器端人脸检查与裁剪、20 分钟超时退款）；加署名和 /about/ 页。
- 第 3 项：品牌名统一为 Tiny Desk Trend，schema 里把 Tiny Desk AI 写作 alternateName。
- 第 4 项：样片从 2.8 MB 压到 0.94 MB，进入视口才加载播放。
- 第 5 项：加了 Organization、BreadcrumbList、ItemList、CollectionPage、AboutPage、VideoObject；Article 补了 author、image、publisher.logo。
- 第 6 项：FAQ 每个回答下加了延伸链接；每篇教程末尾加生成入口和 3 篇相关教程；页面顶部加面包屑。
- 第 7 项：/guides/ 每篇配一句摘要，description 重写。
- 第 8 项：按新设计生成分享图，首页和每篇教程各一张。
- 第 9 项（部分）：竞品出处改标为“二手来源”并说明原因；时间线加入 NPR 和 Wikipedia 一手来源，以及我们自己的 Trends 监测数据。TikTok 原帖链接仍未找到。
- 第 10–13 项：description 控制在 155 字符以内；sitemap 的 lastmod 按真实修改日期写；首页不再输出 FAQPage schema；robots.txt 屏蔽 /api/。

未处理：第 14 项（Cloudflare 统计脚本被 CSP 拦截），需要先决定要不要统计。
