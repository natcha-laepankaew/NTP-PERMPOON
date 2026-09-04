import type { VehicleStatus } from "../services/api";

export const statusMeta: Record<
  VehicleStatus,
  { label: string; sub: string; color: string }
> = {
  AVAILABLE: { label: "AVAILABLE", sub: "พร้อมรับงาน", color: "green" },
  BUSY: { label: "BUSY", sub: "กำลังทำงาน", color: "amber" },
  AVAILABLE_RETURN: {
    label: "AVAILABLE_RETURN",
    sub: "พร้อมรับงานขากลับ",
    color: "blue",
  },
  NOT_READY: { label: "NOT_READY", sub: "ไม่พร้อมรับงาน", color: "red" },
  MAINTENANCE: { label: "MAINTENANCE", sub: "ซ่อมบำรุง", color: "slate" },
};
