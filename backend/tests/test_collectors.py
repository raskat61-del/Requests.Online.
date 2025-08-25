import pytest
from unittest.mock import Mock, patch, AsyncMock
import aiohttp

from app.collectors.base import BaseCollector, SearchResult
from app.collectors.google import GoogleCollector
from app.collectors.yandex import YandexCollector
from app.collectors.web_scraper import WebScraper


class TestBaseCollector:
    """Test base collector functionality"""

    @pytest.mark.asyncio
    @pytest.mark.collectors
    async def test_base_collector_abstract_methods(self):
        """Test that BaseCollector cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseCollector()

    @pytest.mark.asyncio
    @pytest.mark.collectors
    async def test_search_result_creation(self):
        """Test SearchResult dataclass creation"""
        result = SearchResult(
            title="Test Title",
            content="Test content",
            url="https://example.com",
            author="Test Author",
            source_type="test"
        )
        
        assert result.title == "Test Title"
        assert result.content == "Test content"
        assert result.url == "https://example.com"
        assert result.author == "Test Author"
        assert result.source_type == "test"

    @pytest.mark.asyncio
    @pytest.mark.collectors
    async def test_clean_text_method(self):
        """Test text cleaning functionality"""
        # Create a mock collector to test the clean_text method
        class TestCollector(BaseCollector):
            async def search(self, query: str, limit: int = 10, **kwargs):
                return []
        
        async with TestCollector() as collector:
            # Test normal text
            clean = collector.clean_text("  Normal text with   spaces  ")
            assert clean == "Normal text with spaces"
            
            # Test text with newlines
            clean = collector.clean_text("Text\nwith\nnewlines")
            assert clean == "Text with newlines"
            
            # Test empty text
            clean = collector.clean_text("")
            assert clean == ""
            
            # Test None
            clean = collector.clean_text(None)
            assert clean == ""


class TestGoogleCollector:
    """Test Google Search collector"""

    @pytest.mark.asyncio
    @pytest.mark.collectors
    @patch('aiohttp.ClientSession.get')
    async def test_google_search_success(self, mock_get):
        """Test successful Google search"""
        # Mock response data
        mock_response_data = {
            "items": [
                {
                    "title": "Test Result 1",
                    "snippet": "Test snippet 1",
                    "link": "https://example1.com"
                },
                {
                    "title": "Test Result 2",
                    "snippet": "Test snippet 2", 
                    "link": "https://example2.com"
                }
            ]
        }
        
        # Configure mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Test
        async with GoogleCollector() as collector:
            results = await collector.search("test query", limit=5)
            
            assert len(results) == 2
            assert results[0].title == "Test Result 1"
            assert results[0].content == "Test snippet 1"
            assert results[0].url == "https://example1.com"
            assert results[0].source_type == "google"

    @pytest.mark.asyncio
    @pytest.mark.collectors
    @patch('aiohttp.ClientSession.get')
    async def test_google_search_no_results(self, mock_get):
        """Test Google search with no results"""
        mock_response_data = {"items": []}
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with GoogleCollector() as collector:
            results = await collector.search("no results query")
            
            assert len(results) == 0

    @pytest.mark.asyncio
    @pytest.mark.collectors
    @patch('aiohttp.ClientSession.get')
    async def test_google_search_api_error(self, mock_get):
        """Test Google search API error handling"""
        mock_response = AsyncMock()
        mock_response.status = 403  # API quota exceeded
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with GoogleCollector() as collector:
            results = await collector.search("test query")
            
            assert len(results) == 0

    @pytest.mark.asyncio
    @pytest.mark.collectors
    async def test_google_search_no_api_key(self):
        """Test Google search without API key"""
        with patch('app.core.config.settings.GOOGLE_API_KEY', None):
            async with GoogleCollector() as collector:
                results = await collector.search("test query")
                
                assert len(results) == 0


class TestYandexCollector:
    """Test Yandex Search collector"""

    @pytest.mark.asyncio
    @pytest.mark.collectors
    @patch('aiohttp.ClientSession.get')
    async def test_yandex_search_success(self, mock_get):
        """Test successful Yandex search"""
        mock_response_data = {
            "grouping": [{
                "groups": [
                    {
                        "doclist": [{
                            "title": {"__hl": [{"text": "Yandex Test Result"}]},
                            "url": "https://yandex-example.com",
                            "content": {"__hl": [{"text": "Yandex test snippet"}]}
                        }]
                    }
                ]
            }]
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with YandexCollector() as collector:
            results = await collector.search("test query", limit=5)
            
            assert len(results) == 1
            assert "Yandex Test Result" in results[0].title
            assert "Yandex test snippet" in results[0].content
            assert results[0].url == "https://yandex-example.com"
            assert results[0].source_type == "yandex"

    @pytest.mark.asyncio
    @pytest.mark.collectors
    @patch('aiohttp.ClientSession.get')
    async def test_yandex_search_no_results(self, mock_get):
        """Test Yandex search with no results"""
        mock_response_data = {"grouping": [{"groups": []}]}
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with YandexCollector() as collector:
            results = await collector.search("no results query")
            
            assert len(results) == 0


class TestWebScraper:
    """Test web scraping functionality"""

    @pytest.mark.asyncio
    @pytest.mark.collectors
    @patch('aiohttp.ClientSession.get')
    async def test_scrape_webpage_success(self, mock_get):
        """Test successful webpage scraping"""
        mock_html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Test Heading</h1>
                <p>Test paragraph content.</p>
                <a href="https://example.com">Test link</a>
            </body>
        </html>
        """
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with WebScraper() as scraper:
            results = await scraper.search("https://example.com")
            
            assert len(results) == 1
            assert results[0].title == "Test Page"
            assert "Test Heading" in results[0].content
            assert "Test paragraph content" in results[0].content
            assert results[0].url == "https://example.com"
            assert results[0].source_type == "web"

    @pytest.mark.asyncio
    @pytest.mark.collectors
    @patch('aiohttp.ClientSession.get')
    async def test_scrape_webpage_404(self, mock_get):
        """Test scraping non-existent webpage"""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with WebScraper() as scraper:
            results = await scraper.search("https://nonexistent.com")
            
            assert len(results) == 0

    @pytest.mark.asyncio
    @pytest.mark.collectors
    @patch('aiohttp.ClientSession.get')
    async def test_scrape_invalid_html(self, mock_get):
        """Test scraping page with invalid HTML"""
        mock_html = "Invalid HTML content without proper tags"
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with WebScraper() as scraper:
            results = await scraper.search("https://example.com")
            
            assert len(results) == 1
            assert results[0].content == "Invalid HTML content without proper tags"

    @pytest.mark.asyncio
    @pytest.mark.collectors
    @patch('aiohttp.ClientSession.get')
    async def test_extract_text_from_complex_html(self, mock_get):
        """Test text extraction from complex HTML"""
        mock_html = """
        <html>
            <head>
                <title>Complex Page</title>
                <script>alert('remove me');</script>
                <style>body { color: red; }</style>
            </head>
            <body>
                <nav>Navigation menu</nav>
                <main>
                    <article>
                        <h1>Main Article</h1>
                        <p>Important content here.</p>
                        <aside>Sidebar content</aside>
                    </article>
                </main>
                <footer>Footer content</footer>
            </body>
        </html>
        """
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with WebScraper() as scraper:
            results = await scraper.search("https://example.com")
            
            assert len(results) == 1
            content = results[0].content
            
            # Should include main content
            assert "Main Article" in content
            assert "Important content here" in content
            
            # Should not include script or style content
            assert "alert('remove me')" not in content
            assert "color: red" not in content


class TestCollectorRateLimiting:
    """Test rate limiting functionality"""

    @pytest.mark.asyncio
    @pytest.mark.collectors
    @pytest.mark.slow
    async def test_rate_limit_delay(self):
        """Test that collectors respect rate limits"""
        import time
        
        class TestCollector(BaseCollector):
            async def search(self, query: str, limit: int = 10, **kwargs):
                return []
        
        async with TestCollector() as collector:
            start_time = time.time()
            
            # Call rate_limit_delay which should introduce a delay
            await collector.rate_limit_delay()
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Should have at least some delay (depending on settings)
            assert elapsed > 0

    @pytest.mark.asyncio
    @pytest.mark.collectors
    async def test_safe_request_retry_mechanism(self):
        """Test the safe_request retry mechanism"""
        class TestCollector(BaseCollector):
            async def search(self, query: str, limit: int = 10, **kwargs):
                return []
        
        async with TestCollector() as collector:
            with patch.object(collector.session, 'get') as mock_get:
                # Simulate network failure then success
                mock_get.side_effect = [
                    aiohttp.ClientConnectorError("Connection failed"),
                    AsyncMock(status=200)
                ]
                
                # This should retry and eventually succeed
                response = await collector.safe_request("https://example.com")
                
                # Should have made 2 attempts
                assert mock_get.call_count == 2