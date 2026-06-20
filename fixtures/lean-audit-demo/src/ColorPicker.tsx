export function BrandColorPicker({ value, onChange }) {
  return (
    <label>
      Brand color
      <ColorPicker value={value} onChange={onChange} />
    </label>
  );
}
