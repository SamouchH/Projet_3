import { CategoryOption } from '../types';

interface CategoryData {
  CATEGORIES: {
    [key: string]: {
      [key: string]: string[];
    };
  };
}

export const getCategoryOptions = (data: CategoryData): CategoryOption[] => {
  const categories = Object.keys(data.CATEGORIES["Jeux vidéo, console"]);
  return categories.map(category => ({
    label: category,
    value: category
  }));
};

export const getSubcategoryOptions = (data: CategoryData, category: string): CategoryOption[] => {
  const categoryData = data.CATEGORIES["Jeux vidéo, console"][category];
  if (!categoryData) return [];

  return categoryData.map(subcategory => ({
    label: subcategory,
    value: subcategory
  }));
};

export const addCustomCategory = (data: CategoryData, category: string): CategoryData => {
  return {
    ...data,
    CATEGORIES: {
      "Jeux vidéo, console": {
        ...data.CATEGORIES["Jeux vidéo, console"],
        [category]: []
      }
    }
  };
};

export const addCustomSubcategory = (
  data: CategoryData,
  category: string,
  subcategory: string
): CategoryData => {
  const categoryData = data.CATEGORIES["Jeux vidéo, console"][category];
  if (!categoryData) return data;

  return {
    ...data,
    CATEGORIES: {
      "Jeux vidéo, console": {
        ...data.CATEGORIES["Jeux vidéo, console"],
        [category]: [...categoryData, subcategory]
      }
    }
  };
}; 