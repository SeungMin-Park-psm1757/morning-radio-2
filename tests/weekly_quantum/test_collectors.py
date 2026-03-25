from datetime import UTC, datetime

from morning_radio.weekly_quantum.collectors.fqcf import FQCFCollector, IssueEntry
from morning_radio.weekly_quantum.collectors.qcr import QCRCollector
from morning_radio.weekly_quantum.collectors.tqi import TQICollector
from morning_radio.weekly_quantum.collectors.base import SourceConfig


def _source_config(key: str, url: str) -> SourceConfig:
    return SourceConfig(
        key=key,
        label=key,
        start_urls=[url],
        collection_mode="direct",
        kind="test",
        max_items_per_run=10,
    )


def test_qcr_html_parser_extracts_date_title_link_and_excerpt():
    html = """
    <div class="post-content">
      <p>
        <strong>March 16, 2026</strong><br />
        <strong><a href="https://quantumcomputingreport.com/classiq-story/">Classiq Integrates NVIDIA CUDA-Q</a></strong>
        Classiq has integrated its platform with CUDA-Q for hybrid workflows. Read more in our full article
        <a href="https://quantumcomputingreport.com/classiq-story/">here</a>.
      </p>
    </div>
    """
    collector = QCRCollector()
    items = collector._parse_html_list(html, _source_config("qcr_news", "https://quantumcomputingreport.com/news/"))
    assert len(items) == 1
    assert items[0].title == "Classiq Integrates NVIDIA CUDA-Q"
    assert items[0].canonical_url == "https://quantumcomputingreport.com/classiq-story/"
    assert "hybrid workflows" in items[0].excerpt


def test_tqi_html_parser_extracts_title_author_and_date():
    html = """
    <article class="elementor-post">
      <div class="elementor-post__text">
        <h6 class="elementor-post__title">
          <a href="https://thequantuminsider.com/story/">Researchers Demonstrate SUPER Method</a>
        </h6>
        <div class="elementor-post__meta-data">
          <span class="elementor-post-author">Author Name</span>
          <span class="elementor-post-date">March 16, 2026</span>
        </div>
      </div>
    </article>
    """
    collector = TQICollector()
    items = collector._parse_html_list(html, _source_config("tqi_daily", "https://thequantuminsider.com/category/daily/"))
    assert len(items) == 1
    assert items[0].title == "Researchers Demonstrate SUPER Method"
    assert items[0].author == "Author Name"
    assert items[0].canonical_url == "https://thequantuminsider.com/story/"


def test_fqcf_list_parser_extracts_daily_quantum_issue():
    html = """
    <table>
      <tr>
        <td>883</td>
        <td>
          <a href="bbs.php?bbstable=news&call=read&page=1&no=1826">
            [Daily Quantum]2026.3.25 양자기술 뉴스 모음
          </a>
        </td>
        <td>2026-03-25</td>
        <td>관리자</td>
      </tr>
    </table>
    """
    collector = FQCFCollector()
    entries = collector._parse_list_page(html)
    assert len(entries) == 1
    assert entries[0].detail_url.endswith("no=1826")
    assert entries[0].listed_at == datetime(2026, 3, 24, 15, 0, tzinfo=UTC)


def test_fqcf_detail_parser_extracts_external_links(monkeypatch):
    html = """
    <div>By 관리자 posted 2026-03-25 08:49:34 views 6</div>
    <div>국내동향</div>
    <a href="https://example.com/domestic-story">[보안뉴스] 국내 기사 제목</a>
    <div>해외동향</div>
    <a href="https://example.com/global-story">[Quantum Insider] Global quantum story</a>
    <a href="https://www.fqcf.org/">홈</a>
    """
    collector = FQCFCollector()
    monkeypatch.setattr(
        collector,
        "_fetch_external_excerpt",
        lambda url: (f"{url} excerpt", True, True),
    )

    items = collector._parse_detail_page(
        html,
        _source_config("fqcf_daily", "https://www.fqcf.org/niabbs5/bbs.php?bbstable=news"),
        IssueEntry(
            detail_url="https://www.fqcf.org/niabbs5/bbs.php?bbstable=news&call=read&page=1&no=1826",
            title="[Daily Quantum]2026.3.25 양자기술 뉴스 모음",
            listed_at=datetime(2026, 3, 24, 15, 0, tzinfo=UTC),
        ),
    )

    assert len(items) == 2
    assert items[0].source_label == "보안뉴스"
    assert items[0].title == "국내 기사 제목"
    assert items[0].section_key == "domestic"
    assert items[0].detail_fetch_succeeded is True
    assert items[0].published_at == datetime(2026, 3, 24, 23, 49, 34, tzinfo=UTC)
    assert items[1].source_label == "Quantum Insider"
    assert items[1].section_key == "international"
