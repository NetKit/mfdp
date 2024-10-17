from fastapi import (
    Request,
    Response,
    HTTPException, 
    Depends, 
    APIRouter, 
    Cookie, 
    status,
    Form,
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.repositories import repository_scope
from app.services import company_service
from app.models import Manager, Company
from app.core import available_cities, available_seniorities, available_roles, salary_percentiles

import os
import json

from typing import Annotated

current_dir = os.path.dirname(os.path.abspath(__file__))

router = APIRouter()

templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

async def get_current_user(session: Annotated[str, Cookie()] = None):
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    async with repository_scope() as repos:
        user = await repos.manager().find_by_token(session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    return user

@router.get("/")
async def home(request: Request, current_user: Manager = Depends(get_current_user)):
    vacancies = await company_service.get_all_companies_vacancies(current_user.company_id)
    return templates.TemplateResponse("index.html", {"request": request, "user": current_user, "vacancies": vacancies, "salary_percentiles": salary_percentiles})

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    company_name: Annotated[str, Form(...)],
    username: Annotated[str, Form(...)],
    email: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
):
    try:
        await company_service.create_company(company_name, username, email, password)
    except Exception as e:
        return templates.TemplateResponse("register.html", {"request": request, "alert": {"type": "danger", "message": e}})

    return RedirectResponse(url="/login", status_code=303)


@router.get("/login")
async def login_page(request: Request, session: Annotated[str, Cookie()] = None):
    if not session:
        return templates.TemplateResponse("login.html", {"request": request})
    
    user = await company_service.get_manager_by_token(session)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request})

    return RedirectResponse(url="/index")

@router.get("/index")
async def index(request: Request, current_user: Manager = Depends(get_current_user)):
    vacancies = await company_service.get_all_companies_vacancies(current_user.company_id)

    return templates.TemplateResponse("index.html", {"request": request, "vacancies": vacancies})

@router.post("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="session")
    
    return response

@router.post("/token")
async def token(
    response: Response,
    email: Annotated[str, Form()], 
    password: Annotated[str, Form()],
):
    user = await company_service.login(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session", value=user.token)
    
    return response

@router.get("/profile")
async def profile_page(request: Request, current_user: Annotated[str, Depends(get_current_user)]):
    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})

@router.post("/vacancies/{vacancy_id}/delete")
async def delete_vacancy(
    vacancy_id: int,
    current_user: Manager = Depends(get_current_user)
):
    try:
        await company_service.delete_vacancy(current_user.company_id, vacancy_id)
        return RedirectResponse(url="/", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/vacancies/create")
async def create_vacancy_form(request: Request, current_user: Manager = Depends(get_current_user)):
    return templates.TemplateResponse("vacancy_form.html", {
        "request": request,
        "available_locations": available_cities,
        "available_seniorities": available_seniorities,
        "available_roles": available_roles,
    })

@router.post("/vacancies/create")
async def create_vacancy(
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    requirements: str = Form(None),
    languages: str = Form(None),
    currency: str = Form(None),
    country: str = Form(None),
    job_type: str = Form(None),
    salary: int = Form(None),
    location: str = Form(None),
    seniority: str = Form(None),
    role: str = Form(None),
    required_years_of_experience: int = Form(None),
    current_user: Manager = Depends(get_current_user)
):
    vacancy_data = {
        "title": title,
        "description": description,
        "requirements": requirements.split(',') if requirements else None,
        "languages": languages.split(',') if languages else None,
        "currency": currency,
        "country": country,
        "job_type": job_type,
        "company_id": current_user.company_id,
        "salary": salary,
        "location": location,
        "seniority": seniority,
        "required_years_of_experience": required_years_of_experience,
        "role": role,
    }
    
    await company_service.create_vacancy(current_user.company_id, vacancy_data)
    
    return RedirectResponse(url="/", status_code=303)
