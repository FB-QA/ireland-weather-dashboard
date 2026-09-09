# Design Spec: Last Updated Timestamp

**Project:** Ireland Weather Dashboard
**Date:** 2026-02-10
**Designer:** Aria

## Feature Overview

A subtle, informative timestamp that tells the user when weather data was last fetched. It lives quietly beneath the location heading, reinforcing trust in the data without competing for attention.

## Design Direction

This element follows the existing `detail-label` pattern — small, secondary, utility-driven. It should feel like it has always been there. No new visual language, no new colors. Just the right information at the right size in the right place, using the dashboard's established typographic hierarchy for metadata.

## Component Plan

| Component | Status | Notes |
|-----------|--------|-------|
| `.last-updated` | **New** | Timestamp line below location heading |

### New Components

#### `.last-updated`

A single-line timestamp positioned directly below `.location-heading` and above the current conditions card. Uses existing secondary text color and 0.8125rem (13px) type size — same scale as footer/divider text.

**HTML structure:**
```html
<p class="last-updated" id="last-updated" aria-live="polite" aria-atomic="true">
  Updated <time datetime="2026-02-10T15:42:00">3:42 PM</time>
</p>
```

### Modified Components
None.

## Layout

```
Location Heading ("Dublin")       .location-heading (existing)
                       8px gap
Updated 3:42 PM                   .last-updated (new)
                      20px gap
Current Conditions Card           .current-weather-card (existing)
```

Left-aligned with location heading. No icon, no decoration.

### Responsive Behaviour

| Breakpoint | Margin |
|------------|--------|
| Default (>640px) | `-12px 0 20px 0` |
| 640px | `-8px 0 16px 0` |
| 380px | No change |

## States & Interactions

| Element | Default | Loading | Error | Empty |
|---------|---------|---------|-------|-------|
| `.last-updated` | Hidden (opacity: 0) | "Updating..." with pulse | Retains last timestamp | Hidden |

### Transitions & Motion

- Show/hide: opacity + translateY(4px), 200ms ease
- Loading pulse: opacity 0.5 → 1, 1.2s ease-in-out infinite

## Accessibility
- `aria-live="polite"`, `aria-atomic="true"`
- `<time>` element with `datetime` attribute
- Contrast: `#64748b` on `#ffffff` = 4.53:1 (passes AA)

## Implementation Notes

### CSS
```css
.last-updated {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  font-weight: 400;
  margin: -12px 0 20px 0;
  line-height: 1;
  opacity: 0;
  transform: translateY(-4px);
  transition: opacity var(--transition), transform var(--transition);
}
.last-updated.visible { opacity: 1; transform: translateY(0); }
.last-updated.loading { animation: pulse-opacity 1.2s ease-in-out infinite; }
@keyframes pulse-opacity { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }
```

### Time Format
- 12-hour, no leading zero, AM/PM: "3:42 PM"
- Use `en-IE` locale with `toLocaleTimeString`
- `hour: 'numeric'`, `minute: '2-digit'`, `hour12: true`
