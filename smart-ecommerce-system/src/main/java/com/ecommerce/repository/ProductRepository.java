package com.ecommerce.repository;

import com.ecommerce.entity.Product;
import com.ecommerce.entity.Category;
import com.ecommerce.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    
    Page<Product> findByActiveTrue(Pageable pageable);
    
    Page<Product> findByCategoryAndActiveTrue(Category category, Pageable pageable);
    
    Page<Product> findBySellerAndActiveTrue(User seller, Pageable pageable);
    
    List<Product> findByActiveTrue();
    
    List<Product> findByCategoryAndActiveTrue(Category category);
    
    List<Product> findBySellerAndActiveTrue(User seller);
    
    @Query("SELECT p FROM Product p WHERE p.active = true AND p.name LIKE %:keyword% OR p.description LIKE %:keyword%")
    Page<Product> findByKeyword(@Param("keyword") String keyword, Pageable pageable);
    
    @Query("SELECT p FROM Product p WHERE p.active = true AND p.price BETWEEN :minPrice AND :maxPrice")
    Page<Product> findByPriceRange(@Param("minPrice") BigDecimal minPrice, 
                                   @Param("maxPrice") BigDecimal maxPrice, Pageable pageable);
    
    @Query("SELECT p FROM Product p WHERE p.active = true ORDER BY p.price ASC")
    Page<Product> findAllByOrderByPriceAsc(Pageable pageable);
    
    @Query("SELECT p FROM Product p WHERE p.active = true ORDER BY p.price DESC")
    Page<Product> findAllByOrderByPriceDesc(Pageable pageable);
    
    @Query("SELECT p FROM Product p WHERE p.active = true ORDER BY p.createdAt DESC")
    Page<Product> findAllByOrderByCreatedAtDesc(Pageable pageable);
}