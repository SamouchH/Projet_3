import { useState, useEffect } from 'react';
import { CategoryOption } from '../../types';
import { isImageFile, readImageFile } from '../../utils/fileUtils';
import { Upload, ChevronLeft, ChevronRight, Save, Download, ChevronDown } from 'lucide-react';
import { getCategoryOptions, getSubcategoryOptions, getSubSubcategoryOptions } from '../../utils/categoryUtils';
import categoriesData from '../../list.json';

interface ImageData {
  file: File;
  url: string;
  category: string;
  subcategory: string;
  subsubcategory: string;
}

export const ImageLabeler = () => {
  const [images, setImages] = useState<ImageData[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [category, setCategory] = useState<string>('');
  const [subcategory, setSubcategory] = useState<string>('');
  const [subsubcategory, setSubsubcategory] = useState<string>('');

  const categoryOptions = getCategoryOptions(categoriesData);
  const subcategoryOptions = getSubcategoryOptions(categoriesData, category);
  const subsubcategoryOptions = getSubSubcategoryOptions(categoriesData, category, subcategory);

  // Reset dependent fields when parent category changes
  useEffect(() => {
    setSubcategory('');
    setSubsubcategory('');
  }, [category]);

  useEffect(() => {
    setSubsubcategory('');
  }, [subcategory]);

  // Load saved progress from localStorage
  useEffect(() => {
    const savedData = localStorage.getItem('imageLabelerData');
    if (savedData) {
      const { images: savedImages, currentIndex: savedIndex } = JSON.parse(savedData);
      setImages(savedImages);
      setCurrentIndex(savedIndex);
      if (savedImages[savedIndex]) {
        setCategory(savedImages[savedIndex].category || '');
        setSubcategory(savedImages[savedIndex].subcategory || '');
        setSubsubcategory(savedImages[savedIndex].subsubcategory || '');
      }
    }
  }, []);

  // Save progress to localStorage
  useEffect(() => {
    if (images.length > 0) {
      localStorage.setItem('imageLabelerData', JSON.stringify({
        images,
        currentIndex
      }));
    }
  }, [images, currentIndex]);

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files?.length) return;

    const newImages: ImageData[] = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (isImageFile(file)) {
        const url = await readImageFile(file);
        newImages.push({
          file,
          url,
          category: '',
          subcategory: '',
          subsubcategory: ''
        });
      }
    }

    setImages(newImages);
    setCurrentIndex(0);
  };

  const handleSave = () => {
    const updatedImages = [...images];
    updatedImages[currentIndex] = {
      ...updatedImages[currentIndex],
      category,
      subcategory,
      subsubcategory
    };
    setImages(updatedImages);
  };

  const handlePrevious = () => {
    handleSave();
    setCurrentIndex(Math.max(0, currentIndex - 1));
  };

  const handleNext = () => {
    handleSave();
    setCurrentIndex(Math.min(images.length - 1, currentIndex + 1));
  };

  const exportToCSV = () => {
    handleSave();
    const csvContent = [
      ['image_name', 'category', 'subcategory', 'subsubcategory', 'json_format'],
      ...images.map(img => [
        img.file.name,
        img.category,
        img.subcategory,
        img.subsubcategory,
        JSON.stringify({
          category: img.category,
          subcategory: img.subcategory,
          subsubcategory: img.subsubcategory
        })
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'image_labels.csv';
    link.click();
  };

  const Select = ({ 
    value, 
    onChange, 
    options, 
    placeholder,
    disabled = false 
  }: { 
    value: string; 
    onChange: (value: string) => void; 
    options: CategoryOption[];
    placeholder: string;
    disabled?: boolean;
  }) => (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={`w-full px-3 py-1.5 border rounded-md appearance-none bg-white text-sm
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'cursor-pointer'}
          focus:ring-1 focus:ring-blue-500 focus:border-blue-500`}
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
    </div>
  );

  return (
    <div className="flex w-full gap-4">
      {/* Left side - Form */}
      <div className="w-1/4 bg-white rounded-lg shadow p-4 flex flex-col">
        {/* File Upload Section */}
        <div className="mb-4">
          <div className="relative">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              multiple
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
            />
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-blue-500 transition-colors">
              <Upload className="mx-auto h-8 w-8 text-gray-400 mb-1" />
              <p className="text-sm text-gray-600">Drop images here</p>
              <p className="text-xs text-gray-500">Supports multiple images</p>
            </div>
          </div>
        </div>

        {/* Form Fields */}
        <div className="space-y-4 flex-grow">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <Select
              value={category}
              onChange={setCategory}
              options={categoryOptions}
              placeholder="Select category"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subcategory
            </label>
            <Select
              value={subcategory}
              onChange={setSubcategory}
              options={subcategoryOptions}
              placeholder="Select subcategory"
              disabled={!category}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sub-subcategory
            </label>
            <Select
              value={subsubcategory}
              onChange={setSubsubcategory}
              options={subsubcategoryOptions}
              placeholder="Select sub-subcategory"
              disabled={!subcategory}
            />
          </div>
        </div>

        {/* Navigation and Actions */}
        <div className="mt-4 space-y-2">
          <div className="flex justify-between items-center gap-2">
            <button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              className="flex items-center px-2 py-1.5 bg-white border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
              Prev
            </button>
            <button
              onClick={handleSave}
              className="flex items-center px-3 py-1.5 bg-blue-500 text-white text-sm rounded-md hover:bg-blue-600"
            >
              <Save className="w-4 h-4 mr-1" />
              Save
            </button>
            <button
              onClick={handleNext}
              disabled={currentIndex === images.length - 1}
              className="flex items-center px-2 py-1.5 bg-white border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <button
            onClick={exportToCSV}
            disabled={images.length === 0}
            className="w-full flex items-center justify-center px-3 py-1.5 bg-green-500 text-white text-sm rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4 mr-1" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Right side - Image Preview */}
      <div className="w-3/4 bg-white rounded-lg shadow p-4">
        {images[currentIndex] ? (
          <img
            src={images[currentIndex].url}
            alt={`Image ${currentIndex + 1}`}
            className="w-full h-[calc(100vh-8rem)] object-contain rounded-lg"
          />
        ) : (
          <div className="flex items-center justify-center h-[calc(100vh-8rem)] bg-gray-50 rounded-lg">
            <p className="text-gray-500 text-sm">No image selected</p>
          </div>
        )}
      </div>
    </div>
  );
}; 