# WeRead Data Collection

## API Setup
- Endpoint: `POST https://i.weread.qq.com/api/agent/gateway`
- Auth: `Authorization: Bearer $WEREAD_API_KEY`
- Every request: `"skill_version": "1.0.4"` in body
- ⚠️ Business params FLAT at body top level — NOT nested in `params`

## Step 1: Reading Stats

```
api_name: "/readdata/detail"
mode: "monthly"                    # weekly|monthly|annually|overall
baseTime: <timestamp>              # optional, for historical months
```

Call twice: current month (no baseTime) + previous month (baseTime = first day of prev month timestamp).

**Key fields extracted:**
- `totalReadTime` — SECONDS. Convert to "X小时Y分钟". This is the authoritative total.
- `readDays` — days with ≥1 min reading
- `dayAverageReadTime` — seconds, averaged over calendar days (NOT readDays)
- `compare` — vs previous period ratio. 0.2 = ~20% growth. -1.0 = no previous data.
- `readLongest[]` — top 10 books by readTime (seconds). Each has `.book` (title/author/cover) and `.readTime`.
- `preferCategory[]` — up to 8 categories. Each has `categoryTitle`, `readingTime` (seconds), `readingCount`.
- `preferTime[]` — 24-hour distribution array. ⚠️ Starts from 6:00, NOT 0:00. Index 0 = 6am.
- `readStat[]` — summary strings: "读过", "读完", "阅读", "笔记"

**Time conversion:**
```python
def seconds_to_display(s):
    hours = s // 3600
    minutes = (s % 3600) // 60
    return f"{hours}小时{minutes}分钟"
```

## Step 2: Notebooks (Notes Overview)

```
api_name: "/user/notebooks"
count: 100                         # items per page
lastSort: <int>                    # cursor from previous page's last item.sort
```

Pagination: loop until `hasMore == 0`. Each page pass `lastSort` from last item's `.sort`.

**Per-book calculation:**
```
total_notes = reviewCount + noteCount + bookmarkCount
```
- `reviewCount` = thoughts/reviews (includes inline thoughts + book reviews)
- `noteCount` = highlights (original text marks) — NOT total notes
- `bookmarkCount` = bookmarks (position markers, content not exportable)

⚠️ `noteCount` is highlights only, not total. Never use it as total.

Sort by total_notes descending. Keep top 10 for report.

**Per book fields:** `bookId`, `book.title`, `book.author`, `book.categories[].title`, `book.deepLink`, `markedStatus` (1=reading, 2=finished, 4=read), `readingProgress`, `sort`.

## Step 3: Top 3 Book Highlights

```
api_name: "/book/bookmarklist"
bookId: "<id>"
```

Returns: `updated[]` — highlights (type=1, bookmarks filtered out). Each: `markText`, `chapterUid`, `createTime`, `chapters[]` for chapter names.

Sample up to 8 highlights per book. Group by chapter if possible.

```python
def sample_highlights(updated, max_n=8):
    # If ≤ max_n, take all. If > max_n, take evenly distributed sample.
    if len(updated) <= max_n:
        return updated
    step = len(updated) / max_n
    return [updated[int(i * step)] for i in range(max_n)]
```

## Step 4: Shelf

```
api_name: "/shelf/sync"
```

No params. Returns:
- `books[]` — ebooks with `title`, `author`, `category`, `secret`, `finishReading`, `readUpdateTime`
- `albums[]` — audiobooks (separate from books)
- `mp` — article collection entry (non-empty = +1 shelf item, always private)
- `archive[]` — named booklists. Each: `name`, `bookIds[]`. **These names are mental category signals.**

Shelf count = `books.length + albums.length + (mp non-empty ? 1 : 0)`.

**Archive/书单 names are valuable analysis data** — they reveal how the user organizes their reading mentally (e.g., "技能训练", "精力管理和养成", "时人不知心理学").
