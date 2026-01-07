package com.ecommerce.controller;

import com.ecommerce.dto.CategoryDTO;
import com.ecommerce.exception.ResourceNotFoundException;
import com.ecommerce.service.CategoryService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/categories")
@Tag(name = "Category Management", description = "APIs for managing categories")
public class CategoryController {
    
    @Autowired
    private CategoryService categoryService;
    
    @GetMapping
    @Operation(summary = "Get all categories", description = "Retrieve a paginated list of all categories")
    public ResponseEntity<ApiResponse<Page<CategoryDTO>>> getAllCategories(
            @Parameter(description = "Page number (0-indexed)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Number of items per page") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "Sort by field") @RequestParam(defaultValue = "id") String sortBy,
            @Parameter(description = "Sort direction (asc/desc)") @RequestParam(defaultValue = "asc") String sortDir) {
        
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<CategoryDTO> categories = categoryService.getAllCategories(pageable);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Categories retrieved successfully", categories));
    }
    
    @GetMapping("/{id}")
    @Operation(summary = "Get category by ID", description = "Retrieve a category by its unique ID")
    public ResponseEntity<ApiResponse<CategoryDTO>> getCategoryById(@PathVariable Long id) {
        Optional<CategoryDTO> category = categoryService.getCategoryById(id);
        if (category.isEmpty()) {
            throw new ResourceNotFoundException("Category", id);
        }
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Category retrieved successfully", category.get()));
    }
    
    @GetMapping("/name/{name}")
    @Operation(summary = "Get category by name", description = "Retrieve a category by its name")
    public ResponseEntity<ApiResponse<CategoryDTO>> getCategoryByName(@PathVariable String name) {
        Optional<CategoryDTO> category = categoryService.getCategoryByName(name);
        if (category.isEmpty()) {
            throw new ResourceNotFoundException("Category", "name", name);
        }
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Category retrieved successfully", category.get()));
    }
    
    @PostMapping
    @Operation(summary = "Create a new category", description = "Create a new category in the system")
    public ResponseEntity<ApiResponse<CategoryDTO>> createCategory(@Valid @RequestBody CategoryDTO categoryDTO) {
        CategoryDTO createdCategory = categoryService.createCategory(categoryDTO);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(new ApiResponse<>(HttpStatus.CREATED.value(), "Category created successfully", createdCategory));
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "Update category", description = "Update an existing category by ID")
    public ResponseEntity<ApiResponse<CategoryDTO>> updateCategory(@PathVariable Long id, @Valid @RequestBody CategoryDTO categoryDTO) {
        Optional<CategoryDTO> existingCategory = categoryService.getCategoryById(id);
        if (existingCategory.isEmpty()) {
            throw new ResourceNotFoundException("Category", id);
        }
        CategoryDTO updatedCategory = categoryService.updateCategory(id, categoryDTO);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Category updated successfully", updatedCategory));
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "Delete category", description = "Delete a category by ID")
    public ResponseEntity<ApiResponse<Void>> deleteCategory(@PathVariable Long id) {
        Optional<CategoryDTO> category = categoryService.getCategoryById(id);
        if (category.isEmpty()) {
            throw new ResourceNotFoundException("Category", id);
        }
        categoryService.deleteCategory(id);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Category deleted successfully", null));
    }
    
    @GetMapping("/list")
    @Operation(summary = "Get all categories (non-paginated)", description = "Retrieve all categories without pagination")
    public ResponseEntity<ApiResponse<List<CategoryDTO>>> getAllCategoriesList() {
        List<CategoryDTO> categories = categoryService.getAllCategories();
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Categories retrieved successfully", categories));
    }
}