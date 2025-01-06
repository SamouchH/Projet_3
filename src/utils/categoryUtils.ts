import { CategoryData, CategoryOption } from '../types';

export const getCategoryOptions = (data: CategoryData): CategoryOption[] => {
  const topLevelData = data.CATEGORIES["Jeux vidéo, console"];
  return Object.keys(topLevelData).map(category => ({
    label: category,
    value: category
  }));
};

export const getSubcategoryOptions = (data: CategoryData, category: string): CategoryOption[] => {
  const topLevelData = data.CATEGORIES["Jeux vidéo, console"];
  const categoryData = topLevelData[category];
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
  const topLevelData = data.CATEGORIES["Jeux vidéo, console"];
  const categoryData = topLevelData[category];
  if (!categoryData) return [];

  const subcategoryData = categoryData[subcategory];
  if (!subcategoryData || !Array.isArray(subcategoryData)) return [];

  return subcategoryData.map(item => ({
    label: item,
    value: item
  }));
}; 