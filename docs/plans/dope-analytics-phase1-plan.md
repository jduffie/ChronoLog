# DOPE Analytics Module - Phase 1 Implementation Plan

## Vision Summary

Build a comprehensive analytics system for DOPE (Data On Previous Engagement) data with:
- **Scope**: Statistical analysis, comparative analysis, environmental correlations, historical tracking
- **Audience**: All users (individual shooters, competitive shooters, reloaders)
- **Priority**: Velocity statistics (mean, SD, ES) as primary focus
- **Format**: Interactive dashboards with visualizations
- **Workflow**: Template-based wizard (select sessions → choose analysis type → view results)

## Phase 1 Scope

### Core Features
- ✅ Template selection ("Quick Velocity Check", "Environmental Impact", "Load Development")
- ✅ Session filtering (rifle, cartridge, date range, environmental conditions)
- ✅ Advanced velocity statistics (mean, median, SD, ES, min/max, quartiles)
- ✅ Quality indicators (simplified traffic lights + expandable technical details)
- ✅ Distribution visualization (histogram, box plot)
- ✅ Export (charts as PNG/PDF + data as CSV)

### Deferred to Phase 2
- ❌ Environmental correlations and scatter plots
- ❌ Multi-session comparison charts
- ❌ Historical trending
- ❌ Machine learning predictions

## Architecture Decisions

**Location**: `/dope/analytics/` module (analytics is DOPE-specific)
**Templates**: Hard-coded initially, migrate to database-stored later
**Matching**: Smart defaults with inline override capability
**Caching**: Raw DOPE session queries (simple, effective)
**Quality Indicators**: Statistical + data quality checks with severity levels

## Module Structure

```
dope/
├── analytics/
│   ├── __init__.py
│   ├── analytics_service.py      # Business logic, calculations
│   ├── statistics.py              # Velocity stats, quality checks
│   ├── templates.py               # Analysis templates
│   ├── filters.py                 # Session filtering logic
│   ├── visualizations.py          # Chart generation
│   ├── export.py                  # Export functionality
│   └── test_analytics.py          # Unit tests
└── ...

pages/
└── Analytics.py                    # UI page (uses dope.analytics)
```

## Quality Indicators Design

- 🟢 **Good**: Sample size ≥10, no outliers, normal distribution
- 🟡 **Warning**: Sample size 5-9, or outliers present, or environmental data incomplete
- 🔴 **Issues**: Sample size <5, or multiple quality problems

## Smart Matching Defaults

- **Exact match**: rifle_id + cartridge_id + bullet_id
- **User toggles**: ± 5% bullet weight, ± 10 yards range distance, ± date window

## Implementation Checkpoints

### Checkpoint 1: Foundation & Data Layer
**Goal**: Create module structure and data fetching
- Create `/dope/analytics/` module structure
- Build `analytics_service.py` with DOPE data fetching
- Implement `filters.py` for session filtering
- Write unit tests for filter logic
- **Commit**: "Add DOPE analytics module foundation with filtering"

**Files to create**:
- `dope/analytics/__init__.py`
- `dope/analytics/analytics_service.py`
- `dope/analytics/filters.py`
- `dope/analytics/test_analytics.py` (initial tests)

**Key functionality**:
- `AnalyticsService.__init__(supabase_client)`
- `AnalyticsService.get_sessions_for_analysis(user_id, filters)`
- `SessionFilter` dataclass with filter criteria
- Filter by: rifle_id, cartridge_id, bullet_id, date_range, environmental conditions

### Checkpoint 2: Statistics Engine
**Goal**: Calculate velocity statistics and quality indicators
- Build `statistics.py` with velocity calculations
- Implement quality indicator logic (sample size, outliers, normality)
- Add statistical test functions (Grubbs test, normality tests)
- Write comprehensive unit tests for stats
- **Commit**: "Add velocity statistics and quality indicators"

**Files to create**:
- `dope/analytics/statistics.py`

**Key functionality**:
- `calculate_velocity_stats(measurements)` → dict with mean, median, SD, ES, min, max, quartiles
- `check_data_quality(measurements)` → QualityIndicator object (status, warnings, details)
- `detect_outliers(measurements)` → list of outlier indices
- `test_normality(measurements)` → bool + p-value
- Statistical formulas:
  - ES (Extreme Spread) = max - min
  - SD (Standard Deviation) = population std dev
  - Grubbs test for outliers (α = 0.05)

### Checkpoint 3: Templates
**Goal**: Implement analysis templates
- Build `templates.py` with hard-coded analysis templates
- Implement template configuration system
- Add smart matching defaults with override capability
- Write tests for template logic
- **Commit**: "Add analytics templates system"

**Files to create**:
- `dope/analytics/templates.py`

**Key functionality**:
- `TEMPLATES` constant with template definitions
- `AnalysisTemplate` dataclass (name, filters, visualizations, quality_checks)
- `get_template(name)` → AnalysisTemplate
- `apply_template(template, user_selections)` → configured analysis
- Templates:
  - "Quick Velocity Check": Basic stats + histogram + outlier check
  - "Environmental Impact": Stats by temp range + scatter plots (Phase 2)
  - "Load Development": Comparison chart + ES/SD trends (Phase 2)

### Checkpoint 4: Visualizations
**Goal**: Create charts and visual components
- Build `visualizations.py` with Plotly/Matplotlib charts
- Implement histogram, box plot, stats table
- Add quality indicator UI (traffic lights + expandable details)
- Write tests for chart generation
- **Commit**: "Add analytics visualizations"

**Files to create**:
- `dope/analytics/visualizations.py`

**Key functionality**:
- `create_velocity_histogram(measurements)` → Plotly figure
- `create_box_plot(measurements)` → Plotly figure
- `create_stats_table(stats_dict)` → DataFrame/Streamlit table
- `render_quality_indicator(quality_result)` → Streamlit component
- Quality indicator:
  - Traffic light emoji (🟢🟡🔴)
  - Summary message
  - Expandable technical details (p-values, test results)

### Checkpoint 5: Export
**Goal**: Enable data and chart export
- Build `export.py` for chart images and CSV data
- Implement PNG/PDF chart export
- Add CSV data export with metadata
- Write tests for export functionality
- **Commit**: "Add analytics export functionality"

**Files to create**:
- `dope/analytics/export.py`

**Key functionality**:
- `export_chart_as_image(figure, format='png')` → bytes
- `export_data_as_csv(measurements, stats)` → CSV string with metadata
- Metadata in CSV: analysis date, template used, filters applied, quality indicators
- Streamlit download buttons for exports

### Checkpoint 6: UI Integration
**Goal**: Build Streamlit page and wire everything together
- Create `/pages/Analytics.py` Streamlit page
- Wire up template selection wizard
- Connect filters, stats, visualizations, and export
- Add caching for performance
- Write UI integration tests
- **Commit**: "Add Analytics page with complete workflow"

**Files to create**:
- `pages/Analytics.py`

**Key functionality**:
- Authentication check (require user login)
- Template selection dropdown
- Filter configuration (based on template)
- Session matching configuration
- Results display (stats table + charts + quality indicators)
- Export buttons (chart images + CSV data)
- Caching: `@st.cache_data` for session queries

**UI Flow**:
1. User selects analysis template
2. Configure filters (or use template defaults)
3. Configure matching rules (or use smart defaults)
4. Click "Analyze" button
5. Display results:
   - Quality indicator at top
   - Statistics table
   - Histogram
   - Box plot
   - Export buttons

### Checkpoint 7: Polish & Documentation
**Goal**: Add explanations and documentation
- Add user-friendly explanations for statistical concepts
- Write module documentation (README.md)
- Update CLAUDE.md with analytics patterns
- Add tooltips and help text in UI
- **Commit**: "Polish analytics UI and add documentation"

**Files to create/update**:
- `dope/analytics/README.md`
- `CLAUDE.md` (update with analytics section)

**Documentation to add**:
- README: Module purpose, architecture, usage examples
- CLAUDE.md: Analytics development patterns, testing guidelines
- UI tooltips: Explain SD, ES, Grubbs test, normality test
- Quality indicator explanations for each status level

## Design Patterns to Follow

1. **Three-layer architecture**: Service → Business Logic → UI
2. **Protocol definitions**: Create `dope/analytics/protocols.py` for type safety
3. **Model classes**: Use dataclasses with type hints
4. **User data isolation**: All queries filtered by `user_id`
5. **Metric units**: Store and calculate in metric, convert at display edge
6. **Comprehensive tests**: Unit tests for each module, integration test for workflow
7. **Error handling**: Service layer returns None/empty for "not found", raises for system errors

## Critical Files

**New files to create**:
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/dope/analytics/__init__.py`
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/dope/analytics/analytics_service.py`
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/dope/analytics/statistics.py`
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/dope/analytics/templates.py`
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/dope/analytics/filters.py`
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/dope/analytics/visualizations.py`
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/dope/analytics/export.py`
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/dope/analytics/test_analytics.py`
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/dope/analytics/protocols.py`
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/dope/analytics/README.md`
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/pages/Analytics.py`

**Files to update**:
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/CLAUDE.md`
- `/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/dope/__init__.py` (export analytics API)

## Development Strategy

- **Incremental commits**: Commit after each checkpoint
- **Working checkpoints**: Each component testable independently
- **Stable main branch**: Keep main branch deployable
- **No rush**: Take time to implement properly with tests
- **Test-driven**: Write tests alongside implementation

## Next Steps

When ready to implement:
1. Start with Checkpoint 1 (Foundation & Data Layer)
2. Follow three-layer architecture pattern
3. Write tests for each component
4. Make incremental commits
5. Move to Checkpoint 2 after Checkpoint 1 is complete and tested
