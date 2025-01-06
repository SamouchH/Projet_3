import { CategoryOption } from '../types';

interface CategoryData {
  CATEGORIES: {
    [key: string]: {
      [key: string]: {
        [key: string]: string[];
      };
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

  return Object.keys(categoryData).map(subcategory => ({
    label: subcategory,
    value: subcategory
  }));
};

export const getSubSubcategoryOptions = (
  data: CategoryData,
  category: string,
  subcategory: string
): CategoryOption[] => {
  const categoryData = data.CATEGORIES["Jeux vidéo, console"][category];
  if (!categoryData) return [];

  const subcategoryData = categoryData[subcategory];
  if (!subcategoryData || !Array.isArray(subcategoryData)) return [];

  return subcategoryData.map(item => ({
    label: item,
    value: item
  }));
}; 