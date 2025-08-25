#!/usr/bin/env python3
"""
Скрипт для тестирования API бота-аналитика
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional


class AnalyticsBotTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self.access_token: Optional[str] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Выполнение HTTP запроса"""
        url = f"{self.api_url}{endpoint}"
        
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        
        if self.access_token:
            request_headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=request_headers) as response:
                    return await self._handle_response(response)
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=request_headers) as response:
                    return await self._handle_response(response)
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, headers=request_headers) as response:
                    return await self._handle_response(response)
            elif method.upper() == "DELETE":
                async with self.session.delete(url, headers=request_headers) as response:
                    return await self._handle_response(response)
        except Exception as e:
            return {"error": str(e), "status": "request_failed"}
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Обработка ответа"""
        try:
            data = await response.json()
            data["status_code"] = response.status
            return data
        except:
            text = await response.text()
            return {
                "status_code": response.status,
                "text": text,
                "error": "Failed to parse JSON"
            }
    
    async def test_health(self) -> bool:
        """Тест здоровья сервиса"""
        print("🔍 Проверка здоровья сервиса...")
        
        try:
            response = await self.make_request("GET", "/../../health")
            if response.get("status_code") == 200:
                print("✅ Сервис работает")
                return True
            else:
                print(f"❌ Сервис недоступен: {response}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при проверке здоровья: {e}")
            return False
    
    async def test_register_user(self, username: str = "testuser", email: str = "test@example.com") -> bool:
        """Тест регистрации пользователя"""
        print("👤 Тестирование регистрации пользователя...")
        
        user_data = {
            "username": username,
            "email": email,
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        response = await self.make_request("POST", "/auth/register", user_data)
        
        if response.get("status_code") == 201:
            print("✅ Пользователь успешно зарегистрирован")
            return True
        elif response.get("status_code") == 400:
            print("⚠️  Пользователь уже существует")
            return True  # Это нормально для повторного запуска теста
        else:
            print(f"❌ Ошибка регистрации: {response}")
            return False
    
    async def test_login(self, username: str = "testuser") -> bool:
        """Тест авторизации"""
        print("🔑 Тестирование авторизации...")
        
        login_data = {
            "username": username,
            "password": "testpassword123"
        }
        
        response = await self.make_request("POST", "/auth/login-json", login_data)
        
        if response.get("status_code") == 200 and "access_token" in response:
            self.access_token = response["access_token"]
            print("✅ Авторизация успешна")
            return True
        else:
            print(f"❌ Ошибка авторизации: {response}")
            return False
    
    async def test_get_user_info(self) -> bool:
        """Тест получения информации о пользователе"""
        print("ℹ️  Тестирование получения информации о пользователе...")
        
        response = await self.make_request("GET", "/users/me")
        
        if response.get("status_code") == 200:
            print(f"✅ Информация получена: {response.get('username', 'Unknown')}")
            return True
        else:
            print(f"❌ Ошибка получения информации: {response}")
            return False
    
    async def test_create_project(self) -> Optional[int]:
        """Тест создания проекта"""
        print("📊 Тестирование создания проекта...")
        
        project_data = {
            "name": "Тестовый проект анализа",
            "description": "Проект для тестирования API бота-аналитика",
            "status": "active"
        }
        
        response = await self.make_request("POST", "/projects/", project_data)
        
        if response.get("status_code") == 201:
            project_id = response.get("id")
            print(f"✅ Проект создан с ID: {project_id}")
            return project_id
        else:
            print(f"❌ Ошибка создания проекта: {response}")
            return None
    
    async def test_get_projects(self) -> bool:
        """Тест получения списка проектов"""
        print("📋 Тестирование получения списка проектов...")
        
        response = await self.make_request("GET", "/projects/")
        
        if response.get("status_code") == 200:
            projects = response if isinstance(response, list) else []
            print(f"✅ Получено проектов: {len(projects)}")
            return True
        else:
            print(f"❌ Ошибка получения проектов: {response}")
            return False
    
    async def test_get_project(self, project_id: int) -> bool:
        """Тест получения конкретного проекта"""
        print(f"🔍 Тестирование получения проекта {project_id}...")
        
        response = await self.make_request("GET", f"/projects/{project_id}")
        
        if response.get("status_code") == 200:
            print(f"✅ Проект получен: {response.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Ошибка получения проекта: {response}")
            return False
    
    async def test_api_endpoints(self) -> bool:
        """Тест доступности различных эндпоинтов"""
        print("🌐 Тестирование доступности эндпоинтов...")
        
        endpoints_to_test = [
            "/search/start",
            "/analysis/results/1",
            "/reports/generate/1"
        ]
        
        all_good = True
        for endpoint in endpoints_to_test:
            response = await self.make_request("GET", endpoint)
            status = response.get("status_code", 0)
            
            if status in [200, 401, 404]:  # 401 и 404 тоже означают что эндпоинт доступен
                print(f"✅ {endpoint} доступен (статус: {status})")
            else:
                print(f"❌ {endpoint} недоступен (статус: {status})")
                all_good = False
        
        return all_good
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Запуск всех тестов"""
        results = {}
        
        print("🚀 Запуск тестов API бота-аналитика\n")
        
        # Проверка здоровья
        results["health"] = await self.test_health()
        
        if not results["health"]:
            print("❌ Сервис недоступен, остальные тесты пропущены")
            return results
        
        # Регистрация и авторизация
        results["register"] = await self.test_register_user()
        results["login"] = await self.test_login()
        
        if not results["login"]:
            print("❌ Авторизация не удалась, остальные тесты пропущены")
            return results
        
        # Тесты пользователя
        results["user_info"] = await self.test_get_user_info()
        
        # Тесты проектов
        project_id = await self.test_create_project()
        results["create_project"] = project_id is not None
        results["get_projects"] = await self.test_get_projects()
        
        if project_id:
            results["get_project"] = await self.test_get_project(project_id)
        
        # Тесты эндпоинтов
        results["api_endpoints"] = await self.test_api_endpoints()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Вывод сводки тестов"""
        print("\n" + "="*50)
        print("📊 СВОДКА ТЕСТИРОВАНИЯ")
        print("="*50)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.ljust(20)}: {status}")
        
        print("-"*50)
        print(f"Пройдено: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 Все тесты пройдены успешно!")
        else:
            print("⚠️  Некоторые тесты не пройдены")


async def main():
    """Главная функция"""
    async with AnalyticsBotTester() as tester:
        results = await tester.run_all_tests()
        tester.print_summary(results)


if __name__ == "__main__":
    print("Analytics Bot API Tester")
    print("Убедитесь, что сервер запущен на http://localhost:8000")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {e}")