export interface ImageLabel {
  id: string;
  label: string;
  confidence?: number;
}

export interface LabeledImage {
  file: File;
  labels: ImageLabel[];
}

export interface CategoryData {
  name: string;
  subcategories?: CategoryData[];
}

export interface CategoryOption {
  value: string;
  label: string;
} 