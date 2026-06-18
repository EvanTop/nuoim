# Nuo.im

<p align="center">
  <b>多端单词学习工具 — 打字即记忆，高效学英语</b>
</p>

<p align="center">
  <a href="https://nuo.im">在线体验</a>
</p>

## 简介

Nuo.im 是基于 [TypeWords](https://github.com/zyronon/TypeWords) 二次开发的多端单词学习工具，支持 Web、VSCode 扩展和小程序多端同步。通过「跟打 + 听写 + 自测 + 默写」多种练习模式，结合智能记忆曲线算法（FSRS），帮助用户高效记忆单词和文章。

## 在线地址

<https://nuo.im>

## 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | Nuxt 3 / Vue 3 |
| 语言 | TypeScript |
| CSS | UnoCSS / SCSS |
| 状态管理 | Pinia |
| 国际化 | @nuxtjs/i18n / vue-i18n |
| 包管理 | pnpm workspace (monorepo) |
| VSCode 扩展 | Vite + Vue 3 |
| 部署 | EdgeOne Pages |

## 项目结构

```
nuo.im/
├── apps/
│   ├── nuxt/          # 主站 (nuo.im)
│   └── vscode-web/    # VSCode Web 扩展
├── packages/
│   ├── core/          # 核心组件与逻辑
│   ├── base/          # 基础工具
│   └── libs/          # 公共库
├── pnpm-workspace.yaml
└── package.json
```

## 特性

### 单词练习

- 练习模式: 跟打 / 听写 / 自测 / 默写
- 智能模式: 基于 FSRS 记忆曲线自动安排学习计划
- 自由模式: 无限制自主规划
- 详细单词信息: 音标、发音（美式/英式）、例句、短语、同义词、词根词源、错误统计

### 多词典支持

- 内置多种词典（四级/六级/考研/雅思/托福/GRE 等）
- 支持自定义词典导入

### 多语言界面

- 支持 14 种语言: 简体中文、繁體中文、English、Deutsch、Español、Français、Português、Русский、Українська、日本語、한국어、ไทย、Tiếng Việt、Bahasa Indonesia

### 暗色主题

- 自适应系统主题，支持手动切换明暗模式

### 数据同步

- 支持 Supabase 云端同步学习进度

## 本地开发

```bash
# 安装依赖
pnpm install

# 启动主站开发服务器
pnpm dev

# 启动 VSCode Web 开发服务器
pnpm dev-vscode-web

# 构建主站
pnpm generate

# 构建 VSCode Web
pnpm build-vscode-web
```

> 需要 Node.js >= 18

## 部署

```bash
# 构建静态站点
pnpm generate

# 构建 VSCode Web
pnpm build-vscode-web
```

构建产物位于 `apps/nuxt/dist/` 和 `apps/vscode-web/dist/`。

## 致谢

本项目基于 [TypeWords](https://github.com/zyronon/TypeWords) (typewords.cc) 开源项目二次开发，感谢原作者及社区贡献者的杰出工作。

## License

MIT
