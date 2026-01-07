package com.ecommerce.controller;

import com.ecommerce.dto.ProductDTO;
import com.ecommerce.exception.ResourceNotFoundException;
import com.ecommerce.service.ProductService;
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

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/products")
@Tag(name = "Product Management", description = "APIs for managing products")
public class ProductController {
    
    @Autowired
    private ProductService productService;
    
    @GetMapping
    @Operation(summary = "Get all products", description = "Retrieve a paginated list of all products")
    public ResponseEntity<ApiResponse<Page<ProductDTO>>> getAllProducts(
            @Parameter(description = "Page number (0-indexed)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Number of items per page") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "Sort by field") @RequestParam(defaultValue = "id") String sortBy,
            @Parameter(description = "Sort direction (asc/desc)") @RequestParam(defaultValue = "asc") String sortDir) {
        
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<ProductDTO> products = productService.getActiveProducts(pageable);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Products retrieved successfully", products));
    }
    
    @GetMapping("/all")
    @Operation(summary = "Get all products (including inactive)", description = "Retrieve a paginated list of all products including inactive ones")
    public ResponseEntity<ApiResponse<Page<ProductDTO>>> getAllProductsIncludingInactive(
            @Parameter(description = "Page number (0-indexed)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Number of items per page") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "Sort by field") @RequestParam(defaultValue = "id") String sortBy,
            @Parameter(description = "Sort direction (asc/desc)") @RequestParam(defaultValue = "asc") String sortDir) {
        
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<ProductDTO> products = productService.getAllProducts(pageable);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Products retrieved successfully", products));
    }
    
    @GetMapping("/{id}")
    @Operation(summary = "Get product by ID", description = "Retrieve a product by its unique ID")
    public ResponseEntity<ApiResponse<ProductDTO>> getProductById(@PathVariable Long id) {
        Optional<ProductDTO> product = productService.getProductById(id);
        if (product.isEmpty()) {
            throw new ResourceNotFoundException("Product", id);
        }
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Product retrieved successfully", product.get()));
    }
    
    @PostMapping
    @Operation(summary = "Create a new product", description = "Create a new product in the system")
    public ResponseEntity<ApiResponse<ProductDTO>> createProduct(@Valid @RequestBody ProductDTO productDTO) {
        ProductDTO createdProduct = productService.createProduct(productDTO);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(new ApiResponse<>(HttpStatus.CREATED.value(), "Product created successfully", createdProduct));
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "Update product", description = "Update an existing product by ID")
    public ResponseEntity<ApiResponse<ProductDTO>> updateProduct(@PathVariable Long id, @Valid @RequestBody ProductDTO productDTO) {
        Optional<ProductDTO> existingProduct = productService.getProductById(id);
        if (existingProduct.isEmpty()) {
            throw new ResourceNotFoundException("Product", id);
        }
        ProductDTO updatedProduct = productService.updateProduct(id, productDTO);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Product updated successfully", updatedProduct));
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "Delete product", description = "Delete a product by ID")
    public ResponseEntity<ApiResponse<Void>> deleteProduct(@PathVariable Long id) {
        Optional<ProductDTO> product = productService.getProductById(id);
        if (product.isEmpty()) {
            throw new ResourceNotFoundException("Product", id);
        }
        productService.deleteProduct(id);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Product deleted successfully", null));
    }
    
    @GetMapping("/category/{categoryId}")
    @Operation(summary = "Get products by category", description = "Retrieve products by their category ID")
    public ResponseEntity<ApiResponse<Page<ProductDTO>>> getProductsByCategory(
            @PathVariable Long categoryId,
            @Parameter(description = "Page number (0-indexed)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Number of items per page") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "Sort by field") @RequestParam(defaultValue = "id") String sortBy,
            @Parameter(description = "Sort direction (asc/desc)") @RequestParam(defaultValue = "asc") String sortDir) {
        
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<ProductDTO> products = productService.getProductsByCategory(categoryId, pageable);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Products retrieved successfully", products));
    }
    
    @GetMapping("/seller/{sellerId}")
    @Operation(summary = "Get products by seller", description = "Retrieve products by their seller ID")
    public ResponseEntity<ApiResponse<Page<ProductDTO>>> getProductsBySeller(
            @PathVariable Long sellerId,
            @Parameter(description = "Page number (0-indexed)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Number of items per page") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "Sort by field") @RequestParam(defaultValue = "id") String sortBy,
            @Parameter(description = "Sort direction (asc/desc)") @RequestParam(defaultValue = "asc") String sortDir) {
        
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<ProductDTO> products = productService.getProductsBySeller(sellerId, pageable);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Products retrieved successfully", products));
    }
    
    @GetMapping("/search")
    @Operation(summary = "Search products", description = "Search products by keyword in name or description")
    public ResponseEntity<ApiResponse<Page<ProductDTO>>> searchProducts(
            @Parameter(description = "Search keyword") @RequestParam(required = false) String keyword,
            @Parameter(description = "Page number (0-indexed)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Number of items per page") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "Sort by field") @RequestParam(defaultValue = "id") String sortBy,
            @Parameter(description = "Sort direction (asc/desc)") @RequestParam(defaultValue = "asc") String sortDir) {
        
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<ProductDTO> products = productService.searchProducts(keyword, pageable);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Products retrieved successfully", products));
    }
    
    @GetMapping("/price-range")
    @Operation(summary = "Get products by price range", description = "Retrieve products within a specific price range")
    public ResponseEntity<ApiResponse<Page<ProductDTO>>> getProductsByPriceRange(
            @Parameter(description = "Minimum price") @RequestParam(required = false) BigDecimal minPrice,
            @Parameter(description = "Maximum price") @RequestParam(required = false) BigDecimal maxPrice,
            @Parameter(description = "Page number (0-indexed)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Number of items per page") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "Sort by field") @RequestParam(defaultValue = "id") String sortBy,
            @Parameter(description = "Sort direction (asc/desc)") @RequestParam(defaultValue = "asc") String sortDir) {
        
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<ProductDTO> products = productService.getProductsByPriceRange(minPrice, maxPrice, pageable);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Products retrieved successfully", products));
    }
    
    @GetMapping("/sort/price-asc")
    @Operation(summary = "Get products sorted by price ascending", description = "Retrieve products sorted by price in ascending order")
    public ResponseEntity<ApiResponse<Page<ProductDTO>>> getProductsSortedByPriceAsc(
            @Parameter(description = "Page number (0-indexed)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Number of items per page") @RequestParam(defaultValue = "10") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        
        Page<ProductDTO> products = productService.getAllProductsSortedByPriceAsc(pageable);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Products retrieved successfully", products));
    }
    
    @GetMapping("/sort/price-desc")
    @Operation(summary = "Get products sorted by price descending", description = "Retrieve products sorted by price in descending order")
    public ResponseEntity<ApiResponse<Page<ProductDTO>>> getProductsSortedByPriceDesc(
            @Parameter(description = "Page number (0-indexed)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Number of items per page") @RequestParam(defaultValue = "10") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        
        Page<ProductDTO> products = productService.getAllProductsSortedByPriceDesc(pageable);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Products retrieved successfully", products));
    }
    
    @GetMapping("/sort/date-desc")
    @Operation(summary = "Get products sorted by creation date", description = "Retrieve products sorted by creation date in descending order")
    public ResponseEntity<ApiResponse<Page<ProductDTO>>> getProductsSortedByDateDesc(
            @Parameter(description = "Page number (0-indexed)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Number of items per page") @RequestParam(defaultValue = "10") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        
        Page<ProductDTO> products = productService.getAllProductsSortedByDateDesc(pageable);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Products retrieved successfully", products));
    }
}