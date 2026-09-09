You are a Remotion/React developer. Write a complete, valid Remotion composition from this storyboard.

## Storyboard
{{storyboard_json}}

## Brand
Name: {{brand_name}}
Colors: primary={{brand_primary_color}}, secondary={{brand_secondary_color}}, text={{brand_text_color}}

## Requirements
- Single file: src/Root.jsx
- Composition id: "PromoScene"
- 1920x1080, 30fps, 90 frames (3 seconds)
- Use useCurrentFrame() + interpolate() for all animations
- Import from "remotion": Composition, AbsoluteFill, useCurrentFrame, interpolate
- Use the exact brand colors from the config
- Font: monospace for data, sans-serif for headlines
- Export Root as module.exports = { Root }

## Output
Return ONLY the complete JSX code inside a single code block:
```jsx
// complete code here
```

No explanation, no markdown outside the code block.
