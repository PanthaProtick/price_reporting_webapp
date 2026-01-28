# Quality Report Update Feature

## Overview
Users can now **update** their quality reports after initial submission. Previously, quality reports could only be created once and not modified.

## Changes Made

### 1. Backend (routes/user.py)

#### Modified `/create/quality_report/<price_report_id>` Route
- **GET Request**: Now checks if quality report exists and fetches existing data
- **POST Request**: Detects update vs create mode and routes accordingly
- Removed restriction that prevented creating a report if one already exists

#### New Function: `get_existing_quality_data(price_report_id, category)`
- Fetches existing quality report data from database
- Combines data from `quality_reports` table and category-specific table
- Returns merged dictionary with all existing values

#### Updated Process Functions
All four category processing functions now accept `is_update` parameter:
- `process_electronics_quality(price_report_id, category, is_update=False)`
- `process_pharma_quality(price_report_id, category, is_update=False)`
- `process_food_quality(price_report_id, category, is_update=False)`
- `process_apparel_quality(price_report_id, category, is_update=False)`

**Update Logic**:
- If `is_update=True`: Executes UPDATE query on category-specific table
- If `is_update=False`: Executes INSERT queries on both tables
- Quality score is recalculated on every update

### 2. Frontend (templates/create_quality_report.html)

#### Dynamic Title
- Shows "Update Product Quality" when editing
- Shows "Report Product Quality" when creating

#### Pre-fill Support - All Categories
**Electronics**:
- Radio buttons: `device_functional`, `warranty_honored`, `accessories_complete`
- Dropdowns: `authenticity_confidence`, `condition_match`
- Textarea: `reported_issue`

**Pharma**:
- Radio buttons: `packaging_sealed`, `expiry_date_present`, `dosage_label_matches_expected`, `physical_anomalies_present`
- Dropdowns: `expiry_status`, `label_completeness`
- Text input: `evidence_photos`

**Food**:
- Radio buttons: `packaging_intact`, `weight_or_volume_matches_label`, `visible_spoilage_present`, `abnormal_smell_or_appearance`
- Dropdown: `expiry_status`
- Text input: `evidence_photos`

**Apparel**:
- Radio buttons: `early_wear_present`, `color_or_print_fading`
- Dropdowns: `material_quality`, `stitching_quality`, `fit_consistency`
- Text input: `evidence_photos`

#### Dynamic Submit Button
- Shows "Update Quality Report" when editing
- Shows "Submit Quality Report" when creating

### 3. User Interface (templates/user_price_reports.html)

#### Quality Report Column
- **Before**: "Submitted" badge (static, no interaction)
- **After**: "Edit Review" button (green outline) - allows editing
- "Add Review" button remains for reports without quality data

## User Flow

### Creating Quality Report (New)
1. User views price reports at `/user/price_reports`
2. Clicks "Add Review" button
3. Fills out category-specific form
4. Submits → Quality report created
5. Success message: "Quality report submitted successfully!"

### Updating Quality Report (New Feature)
1. User views price reports at `/user/price_reports`
2. Clicks "Edit Review" button for existing quality report
3. Form loads with **pre-filled data**
4. User modifies any fields
5. Clicks "Update Quality Report"
6. Quality score is recalculated
7. Database updated with new values
8. Success message: "Quality report updated successfully!"

## Database Operations

### CREATE (INSERT)
```sql
-- Insert into quality_reports
INSERT INTO quality_reports (price_report_id, user_id, category) 
VALUES (?, ?, ?)

-- Insert into category-specific table
INSERT INTO electronics_quality_reports (...) 
VALUES (...)
```

### UPDATE
```sql
-- Update category-specific table only
UPDATE electronics_quality_reports 
SET device_functional = ?, 
    authenticity_confidence = ?, 
    normalized_quality_score = ?
WHERE quality_report_id = ?
```

**Note**: The main `quality_reports` table record is NOT updated (maintains original timestamp and metadata).

## Security & Validation

✓ **Ownership Check**: Verified that price report belongs to current user  
✓ **Existence Check**: Quality report must exist for updates  
✓ **Required Fields**: Form validation ensures all mandatory fields filled  
✓ **Data Type Validation**: Try-except blocks catch invalid conversions  
✓ **SQL Injection Prevention**: Parameterized queries used throughout

## Benefits

1. **Error Correction**: Users can fix mistakes in original submissions
2. **Updated Assessments**: Quality can change over time (e.g., product deteriorates)
3. **Better Data Quality**: Users more likely to submit if they know they can edit
4. **User Experience**: More forgiving, less pressure to be perfect on first try

## Future Enhancements (Not Implemented)

- [ ] Track update history (revision tracking)
- [ ] Add "updated_at" timestamp to quality_reports table
- [ ] Show version history to users
- [ ] Admin audit trail for quality report changes
- [ ] Confidence score adjustment based on update frequency
