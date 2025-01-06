export interface ImageLabel {
  id: string;
  label: string;
  confidence?: number;
}

export interface LabeledImage {
  file: File;
  labels: ImageLabel[];
}

export interface SubCategory {
  [key: string]: string[];
}

export interface Category {
  [key: string]: SubCategory;
}

export interface CategoryData {
  CATEGORIES: {
    "Jeux vidéo, console": {
      [key: string]: {
        [key: string]: string[];
      };
    };
  };
}

export type CategoryOption = {
  label: string;
  value: string;
}; 