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
