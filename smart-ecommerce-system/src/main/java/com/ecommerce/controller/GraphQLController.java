package com.ecommerce.controller;

import com.ecommerce.dto.CategoryDTO;
import com.ecommerce.dto.ProductDTO;
import com.ecommerce.dto.UserDTO;
import com.ecommerce.entity.User;
import com.ecommerce.service.CategoryService;
import com.ecommerce.service.ProductService;
import com.ecommerce.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.stereotype.Controller;

import java.util.List;
import java.util.Optional;

@Controller
public class GraphQLController {
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private ProductService productService;
    
    @Autowired
    private CategoryService categoryService;
    
    // User Queries
    @QueryMapping
    public UserDTO user(@Argument Long id) {
        Optional<UserDTO> user = userService.getUserById(id);
        return user.orElse(null);
    }
    
    @QueryMapping
    public List<UserDTO> users(@Argument Integer page, @Argument Integer size) {
        // Default to page 0, size 10 if not provided
        int pageNum = (page != null) ? page : 0;
        int pageSize = (size != null) ? size : 10;
        
        return userService.getAllUsers(
                org.springframework.data.domain.PageRequest.of(pageNum, pageSize)
        ).getContent();
    }
    
    @QueryMapping
    public UserDTO userByUsername(@Argument String username) {
        Optional<UserDTO> user = userService.getUserByUsername(username);
        return user.orElse(null);
    }
    
    @QueryMapping
    public UserDTO userByEmail(@Argument String email) {
        Optional<UserDTO> user = userService.getUserByEmail(email);
        return user.orElse(null);
    }
    
    // Product Queries
    @QueryMapping
    public ProductDTO product(@Argument Long id) {
        Optional<ProductDTO> product = productService.getProductById(id);
        return product.orElse(null);
    }
    
    @QueryMapping
    public List<ProductDTO> products(@Argument Integer page, @Argument Integer size) {
        int pageNum = (page != null) ? page : 0;
        int pageSize = (size != null) ? size : 10;
        
        return productService.getActiveProducts(
                org.springframework.data.domain.PageRequest.of(pageNum, pageSize)
        ).getContent();
    }
    
    @QueryMapping
    public List<ProductDTO> productsByCategory(@Argument Long categoryId, @Argument Integer page, @Argument Integer size) {
        int pageNum = (page != null) ? page : 0;
        int pageSize = (size != null) ? size : 10;
        
        return productService.getProductsByCategory(categoryId,
                org.springframework.data.domain.PageRequest.of(pageNum, pageSize)
        ).getContent();
    }
    
    @QueryMapping
    public List<ProductDTO> productsBySeller(@Argument Long sellerId, @Argument Integer page, @Argument Integer size) {
        int pageNum = (page != null) ? page : 0;
        int pageSize = (size != null) ? size : 10;
        
        return productService.getProductsBySeller(sellerId,
                org.springframework.data.domain.PageRequest.of(pageNum, pageSize)
        ).getContent();
    }
    
    @QueryMapping
    public List<ProductDTO> searchProducts(@Argument String keyword, @Argument Integer page, @Argument Integer size) {
        int pageNum = (page != null) ? page : 0;
        int pageSize = (size != null) ? size : 10;
        
        return productService.searchProducts(keyword,
                org.springframework.data.domain.PageRequest.of(pageNum, pageSize)
        ).getContent();
    }
    
    // Category Queries
    @QueryMapping
    public CategoryDTO category(@Argument Long id) {
        Optional<CategoryDTO> category = categoryService.getCategoryById(id);
        return category.orElse(null);
    }
    
    @QueryMapping
    public List<CategoryDTO> categories(@Argument Integer page, @Argument Integer size) {
        int pageNum = (page != null) ? page : 0;
        int pageSize = (size != null) ? size : 10;
        
        return categoryService.getAllCategories(
                org.springframework.data.domain.PageRequest.of(pageNum, pageSize)
        ).getContent();
    }
    
    @QueryMapping
    public CategoryDTO categoryByName(@Argument String name) {
        Optional<CategoryDTO> category = categoryService.getCategoryByName(name);
        return category.orElse(null);
    }
    
    // User Mutations
    @MutationMapping
    public UserDTO createUser(@Argument UserInput input) {
        UserDTO userDTO = new UserDTO();
        userDTO.setUsername(input.getUsername());
        userDTO.setEmail(input.getEmail());
        userDTO.setPassword(input.getPassword());
        userDTO.setFirstName(input.getFirstName());
        userDTO.setLastName(input.getLastName());
        userDTO.setRole(User.Role.valueOf(input.getRole() != null ? input.getRole() : "CUSTOMER"));
        userDTO.setEnabled(input.getEnabled() != null ? input.getEnabled() : true);
        
        return userService.createUser(userDTO);
    }
    
    @MutationMapping
    public UserDTO updateUser(@Argument Long id, @Argument UserInput input) {
        UserDTO userDTO = new UserDTO();
        userDTO.setUsername(input.getUsername());
        userDTO.setEmail(input.getEmail());
        userDTO.setPassword(input.getPassword());
        userDTO.setFirstName(input.getFirstName());
        userDTO.setLastName(input.getLastName());
        userDTO.setRole(User.Role.valueOf(input.getRole() != null ? input.getRole() : "CUSTOMER"));
        userDTO.setEnabled(input.getEnabled() != null ? input.getEnabled() : true);
        
        return userService.updateUser(id, userDTO);
    }
    
    @MutationMapping
    public Boolean deleteUser(@Argument Long id) {
        userService.deleteUser(id);
        return true;
    }
    
    // Product Mutations
    @MutationMapping
    public ProductDTO createProduct(@Argument ProductInput input) {
        ProductDTO productDTO = new ProductDTO();
        productDTO.setName(input.getName());
        productDTO.setDescription(input.getDescription());
        productDTO.setPrice(java.math.BigDecimal.valueOf(input.getPrice()));
        productDTO.setQuantity(input.getQuantity());
        productDTO.setImageUrl(input.getImageUrl());
        productDTO.setActive(input.getActive() != null ? input.getActive() : true);
        productDTO.setCategoryId(input.getCategoryId());
        productDTO.setSellerId(input.getSellerId());
        
        return productService.createProduct(productDTO);
    }
    
    @MutationMapping
    public ProductDTO updateProduct(@Argument Long id, @Argument ProductInput input) {
        ProductDTO productDTO = new ProductDTO();
        productDTO.setName(input.getName());
        productDTO.setDescription(input.getDescription());
        productDTO.setPrice(java.math.BigDecimal.valueOf(input.getPrice()));
        productDTO.setQuantity(input.getQuantity());
        productDTO.setImageUrl(input.getImageUrl());
        productDTO.setActive(input.getActive() != null ? input.getActive() : true);
        productDTO.setCategoryId(input.getCategoryId());
        productDTO.setSellerId(input.getSellerId());
        
        return productService.updateProduct(id, productDTO);
    }
    
    @MutationMapping
    public Boolean deleteProduct(@Argument Long id) {
        productService.deleteProduct(id);
        return true;
    }
    
    // Category Mutations
    @MutationMapping
    public CategoryDTO createCategory(@Argument CategoryInput input) {
        CategoryDTO categoryDTO = new CategoryDTO();
        categoryDTO.setName(input.getName());
        categoryDTO.setDescription(input.getDescription());
        categoryDTO.setImageUrl(input.getImageUrl());
        categoryDTO.setActive(input.getActive() != null ? input.getActive() : true);
        
        return categoryService.createCategory(categoryDTO);
    }
    
    @MutationMapping
    public CategoryDTO updateCategory(@Argument Long id, @Argument CategoryInput input) {
        CategoryDTO categoryDTO = new CategoryDTO();
        categoryDTO.setName(input.getName());
        categoryDTO.setDescription(input.getDescription());
        categoryDTO.setImageUrl(input.getImageUrl());
        categoryDTO.setActive(input.getActive() != null ? input.getActive() : true);
        
        return categoryService.updateCategory(id, categoryDTO);
    }
    
    @MutationMapping
    public Boolean deleteCategory(@Argument Long id) {
        categoryService.deleteCategory(id);
        return true;
    }
    
    // Input classes for GraphQL
    public static class UserInput {
        private String username;
        private String email;
        private String password;
        private String firstName;
        private String lastName;
        private String role;
        private Boolean enabled;
        
        // Getters and setters
        public String getUsername() { return username; }
        public void setUsername(String username) { this.username = username; }
        
        public String getEmail() { return email; }
        public void setEmail(String email) { this.email = email; }
        
        public String getPassword() { return password; }
        public void setPassword(String password) { this.password = password; }
        
        public String getFirstName() { return firstName; }
        public void setFirstName(String firstName) { this.firstName = firstName; }
        
        public String getLastName() { return lastName; }
        public void setLastName(String lastName) { this.lastName = lastName; }
        
        public String getRole() { return role; }
        public void setRole(String role) { this.role = role; }
        
        public Boolean getEnabled() { return enabled; }
        public void setEnabled(Boolean enabled) { this.enabled = enabled; }
    }
    
    public static class ProductInput {
        private String name;
        private String description;
        private Double price;
        private Integer quantity;
        private String imageUrl;
        private Boolean active;
        private Long categoryId;
        private Long sellerId;
        
        // Getters and setters
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        
        public Double getPrice() { return price; }
        public void setPrice(Double price) { this.price = price; }
        
        public Integer getQuantity() { return quantity; }
        public void setQuantity(Integer quantity) { this.quantity = quantity; }
        
        public String getImageUrl() { return imageUrl; }
        public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
        
        public Boolean getActive() { return active; }
        public void setActive(Boolean active) { this.active = active; }
        
        public Long getCategoryId() { return categoryId; }
        public void setCategoryId(Long categoryId) { this.categoryId = categoryId; }
        
        public Long getSellerId() { return sellerId; }
        public void setSellerId(Long sellerId) { this.sellerId = sellerId; }
    }
    
    public static class CategoryInput {
        private String name;
        private String description;
        private String imageUrl;
        private Boolean active;
        
        // Getters and setters
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        
        public String getImageUrl() { return imageUrl; }
        public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
        
        public Boolean getActive() { return active; }
        public void setActive(Boolean active) { this.active = active; }
    }
}