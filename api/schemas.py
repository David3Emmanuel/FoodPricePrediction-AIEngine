from pydantic import BaseModel

class PredictionRequest(BaseModel):
    commodity_id: str | None = None
    Food_Item: str | None = None
    Item_Type: str | None = None
    Category: str | None = None
    Vendor_Type: str | None = None

class PredictionResponseMetadata(BaseModel):
    commodity_id: str | None = None
    Food_Item: str | None = None
    Vendor_Type: str | None = None

class TopDrivingFeature(BaseModel):
    feature: str
    current_value: float | str
    impact_percentage: float
    direction: str

class XAIExplanation(BaseModel):
    base_market_trend: float
    top_driving_features: list[TopDrivingFeature]

class PredictionResponse(BaseModel):
    metadata: PredictionResponseMetadata
    forecast_horizon: str
    predicted_price_change_percent: float
    xai_explanation: XAIExplanation

class LivePriceItem(BaseModel):
    commodity_id: str | None = None
    Food_Item: str
    Item_Type: str
    Category: str
    Vendor_Type: str
    State: str
    Price_NGN: float
    Year: int
    Week: int

class LivePricesResponse(BaseModel):
    status: str
    count: int
    prices: list[LivePriceItem]

class SimulationRequest(PredictionRequest):
    Year: int
    Month: int

class SimulationResponseMetadata(BaseModel):
    commodity_id: str | None = None
    Food_Item: str | None = None
    Vendor_Type: str | None = None
    Year: int
    Month: int
    exact_match_found: bool

class SimulationResponse(BaseModel):
    metadata: SimulationResponseMetadata
    forecast_horizon: str
    predicted_price_change_percent: float
    actual_price_change_percent: float | None = None
    error_delta_percent: float | None = None
    xai_explanation: XAIExplanation
