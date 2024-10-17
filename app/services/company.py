from app.repositories.session_manager import repository_scope
from app.models import Company, Manager, Vacancy
from app.workers import scheduler

from typing import Optional, List
from bcrypt import hashpw, gensalt, checkpw
import uuid

class CompanyService:
    async def delete_vacancy(self, company_id: int, vacancy_id: int) -> None:
        async with repository_scope() as repos:
            vacancy = await repos.vacancy().find_by_id(vacancy_id)
            if not vacancy:
                raise ValueError(f'Vacancy with id {vacancy_id} not found')
            
            if vacancy.company_id != company_id:
                raise ValueError('You do not have permission to delete this vacancy')
            
            await repos.vacancy().delete(vacancy.id)

    async def get_manager_by_token(self, token: str) -> Optional[Manager]:
        async with repository_scope() as repos:
            manager = await repos.manager().get_by_token(token)

            return manager

    async def create_company(self, name: str, manager_name: str, manager_email: str, password: str) -> Manager:
        async with repository_scope() as repos:
            company = Company(name=name)
            await repos.company().add(company)

            hashed_password = hashpw(password.encode('utf-8'), gensalt()).decode()
            manager = Manager(name=manager_name, email=manager_email, company=company, password=hashed_password)
            await repos.manager().add(manager)
            
            return manager
    
    async def get_all_companies_vacancies(self, company_id: int) -> List[Vacancy]:
        async with repository_scope() as repos:
            vacancies = await repos.vacancy().find_by_company_id(company_id)
            
        return vacancies

    async def login(self, email: str, password: str) -> Manager:
        async with repository_scope() as repos:
            manager = await repos.manager().find_by_email(email)
            if not manager:
                raise ValueError(f'Manager with email {email} not found')

            if not checkpw(password.encode(), manager.password.encode()):
                raise ValueError('Email or password is incorrect')
            
            manager.token = str(uuid.uuid4())
            manager = await repos.manager().update(manager)
        
        return manager
    
    async def create_vacancy(self, company_id: int, vacancy_data: dict) -> Vacancy:
        async with repository_scope() as repos:
            company = await repos.company().find_by_id(company_id)
            if not company:
                raise ValueError(f'Company with id {company_id} not found')

            vacancy = Vacancy(
                title=vacancy_data['title'],
                description=vacancy_data.get('description'),
                requirements=vacancy_data.get('requirements'),
                languages=vacancy_data.get('languages'),
                currency=vacancy_data.get('currency'),
                country=vacancy_data.get('country'),
                job_type=vacancy_data.get('job_type'),
                salary=vacancy_data.get('salary'),
                location=vacancy_data.get('location'),
                seniority=vacancy_data.get('seniority'),
                role=vacancy_data.get('role'),
                required_years_of_experience=vacancy_data.get('required_years_of_experience'),
                company=company
            )
            await repos.vacancy().add(vacancy)
        
        await scheduler.enqueue("calculate_vacancy_embeddings", [vacancy.id])

        return vacancy


company_service = CompanyService()
