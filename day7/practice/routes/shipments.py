"""
day7/practice/routes/shipments.py — 출고 상태머신 (TODO 빈칸)
================================================================
[과제] complete/routes/work_orders.py 의 패턴을 Shipment 로 옮긴다.

★ 핵심 차이: HOLD 상태 추가 ★

상태 전이도 (5개 상태):

   ┌─────────┐  ship    ┌─────────┐  deliver  ┌───────────┐
   │ PENDING │ ───────▶ │SHIPPING │ ────────▶ │ DELIVERED │
   └────┬────┘          └────┬────┘           └───────────┘
        │ hold              │ return
        ▼                    ▼
   ┌────────┐           ┌──────────┐
   │  HOLD  │ ─resume─▶ │ RETURNED │
   └────┬───┘
        │ cancel
        ▼
   ┌──────────┐
   │ CANCELED │
   └──────────┘
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day7.practice.database import get_db
# TODO 1, 2 완성 후 import 활성화
# from day7.practice.models import Shipment, ShipmentItem, Item, Department, Recipe
# from day7.practice.schemas import ShipmentCreate, ShipmentResponse, ShipmentItemResponse

router = APIRouter(prefix="/shipments", tags=["shipments"])


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 6] ALLOWED_TRANSITIONS dict 정의                       │
# │                                                            │
# │ ALLOWED_TRANSITIONS = {                                    │
# │     "PENDING":   ["SHIPPING", "HOLD", "CANCELED"],          │
# │     "HOLD":      ["PENDING", "CANCELED"],                  │
# │     "SHIPPING":  ["DELIVERED", "RETURNED"],                │
# │     "DELIVERED": [],                                       │
# │     "RETURNED":  [],                                       │
# │     "CANCELED":  [],                                       │
# │ }                                                          │
# │                                                            │
# │ complete 와 비교: HOLD 키 추가 + PENDING 의 다음 상태에    │
# │ HOLD 가 추가됨.                                            │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 7] _check_transition(current, next_) 헬퍼            │
# │                                                            │
# │ 힌트(complete 의 동명 함수 그대로):                        │
# │   if next_ not in ALLOWED_TRANSITIONS.get(current, []):    │
# │       raise HTTPException(400,                             │
# │           f"{current} → {next_} 전이 불가")                │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 8] POST /shipments/ 출고지시 생성                     │
# │                                                            │
# │ 흐름(complete create_work_order 패턴):                     │
# │   1) Item/Department 검증                                  │
# │   2) shipment_number = f"SH-{timestamp}"                   │
# │   3) Shipment INSERT + flush                               │
# │   4) Recipe → ShipmentItem 자동 생성 (quantity 곱셈)        │
# │   5) commit                                                │
# │                                                            │
# │ 자재 소요 = Recipe.quantity × Shipment.quantity            │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 9] PATCH /shipments/{id}/ship 출고 시작 (재고 차감)    │
# │                                                            │
# │ - _check_transition(현재 status, "SHIPPING")               │
# │ - 모든 자재 재고 일괄 검증 → 부족하면 400                  │
# │ - 자재 일괄 차감                                           │
# │ - status="SHIPPING", shipped_at=now                        │
# │                                                            │
# │ 힌트: complete start_work_order 그대로                     │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 10] PATCH /shipments/{id}/hold 보류                   │
# │                                                            │
# │ - _check_transition(현재 status, "HOLD")                   │
# │ - status="HOLD"                                            │
# │ - 자재 변동 없음 (아직 차감 전 상태)                       │
# │                                                            │
# │ 신규 엔드포인트 (complete 에는 없음). HOLD 상태로만 보낼   │
# │ 수 있는 단순 전이.                                         │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 11] PATCH /shipments/{id}/resume HOLD → PENDING      │
# │                                                            │
# │ - _check_transition("HOLD", "PENDING")                     │
# │ - status="PENDING"                                         │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 12] PATCH /shipments/{id}/deliver 배송 완료           │
# │                                                            │
# │ - _check_transition(현재, "DELIVERED")                     │
# │ - status="DELIVERED", delivered_at=now                     │
# │                                                            │
# │ 참고: 출고와 달리 Shipment 는 "완제품 재고 증가" 가 없다.   │
# │       출고는 가져가는 동작이라 추가 재고 변동 없음.        │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 13] PATCH /shipments/{id}/cancel 취소                 │
# │                                                            │
# │ - _check_transition(현재, "CANCELED")                      │
# │ - SHIPPING 상태였다면 차감 자재 원복                       │
# │ - PENDING/HOLD 였다면 자재 변동 없음                       │
# │ - status="CANCELED"                                        │
# │                                                            │
# │ 힌트: complete cancel_work_order 패턴                       │
# │       (단, IN_PROGRESS → SHIPPING 으로 매핑)               │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 14] GET /shipments/ 목록 (status 필터)                │
# │ 힌트: complete list_work_orders, status.upper() 패턴       │
# └──────────────────────────────────────────────────────────┘
