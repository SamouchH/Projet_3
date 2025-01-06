import { useState, useEffect } from 'react';
import { CategoryData, CategoryOption } from '../../types';
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

  const categoryOptions = getCategoryOptions(categoriesData as CategoryData);
  const subcategoryOptions = getSubcategoryOptions(categoriesData as CategoryData, category);
  const subsubcategoryOptions = getSubSubcategoryOptions(categoriesData as CategoryData, category, subcategory);

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
        className={`w-full px-4 py-2 border rounded-lg appearance-none bg-white
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'cursor-pointer'}
          focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
    </div>
  );

  return (
    <div className="flex w-full gap-6">
      {/* Left side - Form */}
      <div className="w-1/3 bg-white rounded-lg shadow-lg p-6 flex flex-col">
        {/* File Upload Section */}
        <div className="mb-8">
          <div className="relative">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              multiple
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
            />
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors">
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-2" />
              <p className="text-sm text-gray-600">Drop images here or click to upload</p>
              <p className="text-xs text-gray-500 mt-1">Supports multiple images</p>
            </div>
          </div>
        </div>

        {/* Form Fields */}
        <div className="space-y-6 flex-grow">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
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
            <label className="block text-sm font-medium text-gray-700 mb-2">
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
            <label className="block text-sm font-medium text-gray-700 mb-2">
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
        <div className="mt-6 space-y-4">
          <div className="flex justify-between items-center">
            <button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              className="flex items-center px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Previous
            </button>
            <button
              onClick={handleSave}
              className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              <Save className="w-4 h-4 mr-1" />
              Save
            </button>
            <button
              onClick={handleNext}
              disabled={currentIndex === images.length - 1}
              className="flex items-center px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
              <ChevronRight className="w-4 h-4 ml-1" />
            </button>
          </div>

          <button
            onClick={exportToCSV}
            className="w-full flex items-center justify-center px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
          >
            <Download className="w-4 h-4 mr-2" />
            Export to CSV
          </button>
        </div>
      </div>

      {/* Right side - Image */}
      <div className="w-2/3 bg-white rounded-lg shadow-lg p-6 flex flex-col">
        {images.length > 0 && currentIndex < images.length ? (
          <>
            <div className="text-sm text-gray-500 mb-4 flex justify-between items-center">
              <span>Image {currentIndex + 1} of {images.length}</span>
              <span className="font-medium">{images[currentIndex].file.name}</span>
            </div>
            <div className="flex-grow flex items-center justify-center bg-gray-50 rounded-lg overflow-hidden">
              <img
                src={images[currentIndex].url}
                alt={`Image ${currentIndex + 1}`}
                className="max-h-full max-w-full object-contain"
              />
            </div>
          </>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-gray-400">
            <Upload className="h-16 w-16 mb-4" />
            <p className="text-lg">No images uploaded</p>
            <p className="text-sm mt-2">Upload images to start labeling</p>
          </div>
        )}
      </div>
    </div>
  );
}; 