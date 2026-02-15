from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.mission import MissionRepository
from app.rules.exceptions import RuleViolation
from app.schemas.mission import MissionCreate, MissionRead
from app.services.mission_service import MissionService

router = APIRouter(prefix="/requests")


@router.post("", response_model=MissionRead, status_code=status.HTTP_201_CREATED)
def create_request(payload: MissionCreate, db: Session = Depends(get_db)) -> MissionRead:
	service = MissionService(db)
	try:
		mission = service.create_mission(payload)
		db.commit()
		return MissionRead.model_validate(mission)
	except RuleViolation as exc:
		db.rollback()
		raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
	except IntegrityError as exc:
		db.rollback()
		raise HTTPException(status_code=409, detail="Request number conflict or invalid references") from exc


@router.get("", response_model=list[MissionRead])
def list_requests(db: Session = Depends(get_db)) -> list[MissionRead]:
	repo = MissionRepository(db)
	return [MissionRead.model_validate(item) for item in repo.list()]


@router.get("/{request_id}", response_model=MissionRead)
def get_request(request_id: int, db: Session = Depends(get_db)) -> MissionRead:
	repo = MissionRepository(db)
	mission = repo.get_with_lines(request_id)
	if mission is None:
		raise HTTPException(status_code=404, detail="Request not found")
	return MissionRead.model_validate(mission)
