# 更新日志

## 2026-03-14 - LRCLIB歌词集成

### 新增功能

#### 1. **LRCLIB歌词源**
- 集成LRCLIB作为主要歌词源
- 免费开源，无需API密钥
- 支持同步歌词（LRC格式）
- 高质量歌词数据库

#### 2. **多源搜索**
- 手动下载时同时显示LRCLIB和网易云的结果
- 用户可以看到每个结果的来源
- 自动按优先级搜索（LRCLIB → 网易云 → 酷狗）

#### 3. **简繁转换**
- LRCLIB获取的歌词自动转换为简体中文
- 使用OpenCC进行转换
- 不影响其他歌词源

### 技术改进

#### `services/lyrics/lyrics_service.py`
- 新增 `_search_from_lrclib()` 方法
- 新增 `_fetch_from_lrclib()` 方法
- 新增 `_download_lrclib_lyrics()` 方法
- 新增 `_convert_to_simplified_chinese()` 方法
- 更新 `search_songs()` 支持多源搜索
- 更新 `_get_online_lyrics()` 优先使用LRCLIB

#### `services/lyrics/lyrics_loader.py`
- `LyricsDownloadWorker` 支持 `lyrics_data` 参数
- 优化手动下载流程，支持预获取的歌词

#### `ui/windows/main_window.py`
- 更新 `_download_lyrics_for_song()` 传递预获取的歌词

### 依赖更新

#### `requirements.txt`
```
+ opencc-python-reimplemented==0.1.7
```

### 测试

- ✅ 所有单元测试通过 (40/40)
- ✅ LRCLIB自动下载功能正常
- ✅ LRCLIB手动下载功能正常
- ✅ 网易云手动下载功能正常
- ✅ 简繁转换功能正常

### 使用说明

#### 自动下载歌词
播放歌曲时，系统会自动按以下顺序搜索歌词：
1. LRCLIB（优先）
2. 网易云云音乐
3. 酷狗

#### 手动下载歌词
1. 点击"下载歌词"按钮
2. 系统显示来自LRCLIB和网易云的搜索结果
3. 选择想要的歌曲
4. 歌词会自动下载并保存

### 注意事项

- LRCLIB不提供封面图片，只有网易云支持下载封面
- 如果OpenCC未安装，歌词保持原样（不转换）
- 已存在的本地.lrc文件优先级最高
