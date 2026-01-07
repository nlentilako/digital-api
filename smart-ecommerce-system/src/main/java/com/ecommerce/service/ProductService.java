package com.ecommerce.service;

import com.ecommerce.dto.ProductDTO;
import com.ecommerce.entity.Category;
import com.ecommerce.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

public interface ProductService {
    
    Page<ProductDTO> getAllProducts(Pageable pageable);
    
    Page<ProductDTO> getActiveProducts(Pageable pageable);
    
    Optional<ProductDTO> getProductById(Long id);
    
    ProductDTO createProduct(ProductDTO productDTO);
    
    ProductDTO updateProduct(Long id, ProductDTO productDTO);
    
    void deleteProduct(Long id);
    
    Page<ProductDTO> getProductsByCategory(Long categoryId, Pageable pageable);
    
    Page<ProductDTO> getProductsBySeller(Long sellerId, Pageable pageable);
    
    List<ProductDTO> getAllActiveProducts();
    
    List<ProductDTO> getProductsByCategory(Long categoryId);
    
    List<ProductDTO> getProductsBySeller(Long sellerId);
    
    Page<ProductDTO> searchProducts(String keyword, Pageable pageable);
    
    Page<ProductDTO> getProductsByPriceRange(BigDecimal minPrice, BigDecimal maxPrice, Pageable pageable);
    
    Page<ProductDTO> getAllProductsSortedByPriceAsc(Pageable pageable);
    
    Page<ProductDTO> getAllProductsSortedByPriceDesc(Pageable pageable);
    
    Page<ProductDTO> getAllProductsSortedByDateDesc(Pageable pageable);
}