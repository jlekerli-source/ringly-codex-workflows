import DatePicker from "react-datepicker";

export function DueDateField({ value, onChange }) {
  return <DatePicker selected={value} onChange={onChange} />;
}
