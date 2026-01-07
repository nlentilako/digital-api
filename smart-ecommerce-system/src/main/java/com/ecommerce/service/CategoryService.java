package com.ecommerce.service;

import com.ecommerce.dto.CategoryDTO;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.Optional;

public interface CategoryService {
    
    Page<CategoryDTO> getAllCategories(Pageable pageable);
    
    Optional<CategoryDTO> getCategoryById(Long id);
    
    Optional<CategoryDTO> getCategoryByName(String name);
    
    CategoryDTO createCategory(CategoryDTO categoryDTO);
    
    CategoryDTO updateCategory(Long id, CategoryDTO categoryDTO);
    
    void deleteCategory(Long id);
    
    List<CategoryDTO> getAllCategories();
    
    boolean existsByName(String name);
}